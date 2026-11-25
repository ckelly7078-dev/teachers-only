"""Stage additional Foundation candidates and audit structure; never promote a record."""
import argparse, csv, hashlib, json, re, sqlite3, subprocess, zipfile
from collections import defaultdict
from pathlib import Path

UNITS = ('M1', 'M2', 'M5', 'M6')
VERSION = 4
HEAD = re.compile(r'^\s{0,12}([1-9]\d?)(?:\s+(\S.*))?\s*$')
PART = re.compile(r'^\(([a-h])\)\s*')
ROMAN = re.compile(r'^\((i{1,3}|iv|v|vi{1,3})\)\s*')
CODE = re.compile(r'(?<![A-Z])(MA|M|A|B)(\d+)\b')
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'zero ten twenty thirty forty fifty sixty seventy eighty ninety'.split()


def expected_count(cover):
    m = re.search(r'answer all ([a-z -]+?) questions', ' '.join(cover.lower().split()))
    if not m: return None
    words = m[1].replace('-', ' ').split()
    if len(words) == 1 and words[0] in ONES: return ONES.index(words[0])
    if len(words) in (1,2) and words[0] in TENS:
        if len(words) == 1: return 10*TENS.index(words[0])
        if words[1] in ONES[:10]: return 10*TENS.index(words[0])+ONES.index(words[1])
    return None


def pages(db, z, sha, raw=False):
    for row in db.execute('SELECT path FROM files WHERE sha=? AND manifest_match=1 ORDER BY path',(sha,)):
        if row[0] in z.NameToInfo:
            if z.getinfo(row[0]).file_size > 32*1024*1024: raise ValueError('Oversize PDF')
            data = z.read(row[0])
            if hashlib.sha256(data).hexdigest() != sha: continue
            run = subprocess.run(['pdftotext','-raw' if raw else '-layout','-enc','UTF-8','-','-'],input=data,capture_output=True,timeout=45,check=True)
            return run.stdout.decode('utf-8').rstrip('\f').split('\f')
    raise ValueError('Source PDF unavailable or hash mismatch')


def anchors(pages, scheme=False):
    records = {}; number = 0; letter = part = ''
    for page, block in enumerate(pages,1):
        if page < 2: continue
        for line in block.splitlines():
            m = HEAD.match(line); text = line.strip()
            if m and int(m[1]) == number+1:
                number += 1; text = (m[2] or '').lstrip(); part = letter = ''
            elif not number: continue
            sub = PART.match(text)
            if sub: letter = part = sub[1]; text = text[sub.end():]
            roman = ROMAN.match(text.strip())
            if roman and letter: part = letter+'.'+roman[1]
            key = (number,part)
            marks = [int(x) for x in re.findall(r'\[(\d{1,2})\]',text)]
            codes = [kind+n for kind,n in CODE.findall(text)]
            if (m and int(m[1]) == number) or sub or roman or (codes if scheme else marks):
                r = records.setdefault(key,dict(page=page,end_page=page,marks=[],codes=[]))
                r['end_page']=page; r['marks'].extend(marks); r['codes'].extend(codes)
    return records


def stage_and_check(db,z,unit):
    output=[]
    for pair in db.execute("SELECT * FROM pairs WHERE unit=? AND status='paired' ORDER BY year,series,component",(unit,)).fetchall():
        paper, scheme = pair['paper'], pair['scheme']
        doc=db.execute('SELECT * FROM documents WHERE sha=?',(paper,)).fetchone()
        row=dict(unit=unit,year=pair['year'],series=pair['series'],component=pair['component'],paper=paper)
        try:
            pp=pages(db,z,paper); sp=pages(db,z,scheme); raw=pages(db,z,paper,True)
            pa,sa=anchors(pp),anchors(sp,True)
            if not pa or not sa: raise ValueError('No anchors on paper or scheme')
            prior=db.execute('SELECT count(*) FROM questions WHERE paper=?',(paper,)).fetchone()[0]
            cover_count=expected_count(pp[0]); observed=max(n for n,p in pa); scheme_count=max(n for n,p in sa)
            layout_marks=sum(sum(v['marks']) for v in pa.values())
            raw_marks=sum(int(x) for block in raw[1:] for x in re.findall(r'\[(\d{1,2})\]',block))
            # Raw extraction is a second text view, not independent visual validation.
            notes=[]
            if cover_count is None or cover_count != observed or scheme_count != observed: notes.append('question count mismatch or missing cover count')
            if layout_marks != doc['total_marks'] or raw_marks != doc['total_marks']: notes.append('candidate mark total mismatch')
            marked=[k for k,v in pa.items() if v['marks']]
            linked=sum(k in sa for k in marked)
            if linked != len(marked): notes.append('some marked parts lack exact scheme anchor')
            if not prior and unit!='M1':
                with db:
                    for (num,part),a in pa.items():
                        s=sa.get((num,part),{})
                        note='Candidate only: source review required.'
                        if notes: note+=' '+ '; '.join(notes)
                        db.execute('INSERT INTO questions(paper,num,part,page,end_page,marks,scheme,scheme_page,codes,extraction_note) VALUES(?,?,?,?,?,?,?,?,?,?)',
                            (paper,num,part,a['page'],a['end_page'],sum(a['marks']) or None,scheme,s.get('page'),json.dumps(s.get('codes',[])),note))
                    db.execute('UPDATE documents SET extracted_version=?,extracted_at=CURRENT_TIMESTAMP WHERE sha IN (?,?)',(VERSION,paper,scheme))
            saved=db.execute('SELECT count(*),sum(marks),sum(status=\'verified\') FROM questions WHERE paper=?',(paper,)).fetchone()
            row.update(cover_questions=cover_count,paper_anchors=observed,scheme_anchors=scheme_count,cover_marks=doc['total_marks'],layout_marks=layout_marks,raw_marks=raw_marks,marked_parts=len(marked),exact_scheme_links=linked,saved_records=saved[0],saved_marks=saved[1],verified=saved[2],status='structural agreement' if not notes else 'review',issues='; '.join(notes))
        except (ValueError,subprocess.SubprocessError,UnicodeError) as e:
            row.update(status='error',issues=str(e))
        output.append(row)
    return output


def refresh_summary(db):
    summary=json.loads(db.execute('SELECT summary FROM state WHERE id=1').fetchone()[0])
    for item in summary:
        u=item['unit']; stats=db.execute('''SELECT count(*),count(q.skill),count(DISTINCT q.skill),count(DISTINCT r.qid),count(DISTINCT CASE WHEN r.qid IS NOT NULL THEN q.skill END) FROM questions q JOIN documents d ON d.sha=q.paper LEFT JOIN postings r ON r.qid=q.id AND r.unit=d.unit AND r.term='*' WHERE d.unit=?''',(u,)).fetchone()
        item.update(questions=stats[0],classified=stats[1],candidate_skills=stats[2],verified=stats[3],covered_skills=stats[4],review=stats[0]-stats[3],skills=db.execute('SELECT count(*) FROM skills WHERE unit=?',(u,)).fetchone()[0],last_extraction=db.execute('SELECT max(extracted_at) FROM documents WHERE unit=? AND extracted_version>0',(u,)).fetchone()[0])
    db.execute('UPDATE state SET revision=revision+1,summary=? WHERE id=1',(json.dumps(summary),))


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--db',required=True); p.add_argument('--archive',required=True); p.add_argument('--unit',choices=UNITS,required=True); p.add_argument('--out',required=True); a=p.parse_args()
    if not Path(a.db).is_file(): raise FileNotFoundError(a.db)
    db=sqlite3.connect(a.db); db.row_factory=sqlite3.Row; db.execute('PRAGMA foreign_keys=ON')
    try:
        with zipfile.ZipFile(a.archive) as z: result=stage_and_check(db,z,a.unit)
        with db:
            refresh_summary(db)
            db.execute('INSERT INTO runs(unit,phase,detail) VALUES(?,?,?)',(a.unit,'structural-audit',json.dumps({s:sum(r['status']==s for r in result) for s in ('structural agreement','review','error')})))
        fields=list(dict.fromkeys(k for r in result for k in r))
        with open(a.out,'w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(result)
        print(a.unit, len(result), 'pairs;',sum(r['status']=='structural agreement' for r in result),'structural agreement;',sum(r['status']=='error' for r in result),'errors;',sum(r.get('saved_records',0) for r in result),'saved records')
    finally: db.close()

if __name__=='__main__': main()
