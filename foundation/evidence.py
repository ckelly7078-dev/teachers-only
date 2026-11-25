"""Bounded runtime retrieval of examiner evidence, separate from marking rules."""
import re

UNITS = ('M1', 'M2', 'M5', 'M6')


def exists(db, table):
    return bool(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone())


def counts(db, unit):
    result = {'reports': 0, 'examiner_anchors': 0, 'examiner_notes': 0, 'examiner_tagged': 0}
    if not exists(db, 'examiner_anchors'):
        return result
    result['reports'], result['examiner_anchors'] = db.execute(
        "SELECT count(DISTINCT report_sha), count(*) FROM examiner_anchors WHERE unit=? AND status='linked'", (unit,)).fetchone()
    result['examiner_notes'] = db.execute("""SELECT count(*) FROM examiner_notes n JOIN examiner_anchors a
       USING(report_sha,unit,component,num) WHERE n.unit=? AND a.status='linked'""", (unit,)).fetchone()[0]
    if exists(db, 'examiner_skill_evidence'):
        result['examiner_tagged'] = db.execute("""SELECT count(*) FROM (SELECT DISTINCT e.report_sha,e.component,e.num
           FROM examiner_skill_evidence e JOIN examiner_anchors a USING(report_sha,unit,component,num)
           WHERE e.unit=? AND a.status='linked')""", (unit,)).fetchone()[0]
    return result


def words(text):
    def stem(w):
        if len(w)>4 and w.endswith('ies'): return w[:-3]+'y'
        if len(w)>3 and w.endswith('s') and not w.endswith(('ss','us')): return w[:-1]
        return w
    return {stem(w) for w in re.findall(r'[a-z0-9]+', text.lower())}


def search(db, unit, query='', limit=8, skill='', paper='', num=None):
    if unit not in UNITS or not isinstance(query,str) or len(query)>160 or type(limit) is not int or not 1<=limit<=12:
        raise ValueError('Invalid examiner search')
    if skill and not db.execute('SELECT 1 FROM skills WHERE unit=? AND id=?',(unit,skill)).fetchone():
        raise ValueError('Unknown skill for unit')
    if paper and (not re.fullmatch(r'[a-f0-9]{64}',paper) or type(num) is not int or not 1<=num<=99):
        raise ValueError('Invalid paper/question reference')
    if not exists(db,'examiner_anchors'):
        return []
    terms=words(query)
    params=[unit]
    where="a.unit=? AND a.status='linked' AND p.status='paired' AND p.paper=a.paper"
    if paper:
        where+=' AND a.paper=? AND a.num=?';params.extend([paper,num])
    # Restrict to linked, date-confirmed sources. No candidate marking rules or PDF text.
    sql="""SELECT a.*,r.filename,r.year,r.series FROM examiner_anchors a JOIN examiner_reports r ON r.sha=a.report_sha
        JOIN pairs p ON p.paper=a.paper AND p.unit=a.unit AND p.component=a.component AND p.year=r.year AND p.series=r.series
        WHERE """+where+" ORDER BY r.year DESC,r.series,a.component,a.num LIMIT 2000"
    tags=exists(db,'examiner_skill_evidence');results=[]
    for a in db.execute(sql,params):
        key=(a['report_sha'],a['unit'],a['component'],a['num'])
        notes=[dict(x) for x in db.execute('SELECT topic,note,review_status FROM examiner_notes WHERE (report_sha,unit,component,num)=(?,?,?,?) ORDER BY topic',key)]
        skills=[dict(x) for x in db.execute('''SELECT e.skill,s.label,s.page AS spec_page,e.status FROM examiner_skill_evidence e
                  JOIN skills s ON s.id=e.skill AND s.unit=e.unit WHERE (e.report_sha,e.unit,e.component,e.num)=(?,?,?,?) ORDER BY s.label''',key)] if tags else []
        if skill and not any(x['skill']==skill for x in skills): continue
        if not notes and not skills and not paper: continue
        note_words=words(' '.join(x['topic']+' '+x['note'] for x in notes))
        skill_words=words(' '.join(x['label']+' '+x['skill'] for x in skills))
        overlap=terms & (note_words|skill_words)
        if terms and not overlap: continue
        score=3*len(terms & note_words)+len(terms & skill_words)
        results.append((score, bool(notes),a['year'],dict(report_sha=a['report_sha'],filename=a['filename'],year=a['year'],series=a['series'],unit=unit,component=a['component'],num=a['num'],start_page=a['start_page'],end_page=a['end_page'],paper=a['paper'],notes=notes,skills=skills,evidence_type='examiner commentary; not a mark scheme')))
    results.sort(key=lambda x:(x[0],x[1],x[2]),reverse=True)
    return [r[3] for r in results[:limit]]
