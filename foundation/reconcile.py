"""Offline coordinate-based Foundation paper/scheme structure audit (not grading).
Requires PyMuPDF; persist only factual metadata and source references, no PDF text.
"""
import argparse
import collections
import csv
import hashlib
import json
import re
import sqlite3
import zipfile
from pathlib import Path

import fitz

# These source-specific mark-label corrections were checked against rendered pages.
# A correction is pinned to the exact source SHA, question and part, and raw marks.
PAPER_FIXES = {
 '879812cdc3c591784071a79978472859be78867fa123ee2b1e51014d29bf37fa': (9,'',[3,3],[3]),
 '1e837bcaa4e6b4e6bb26f9e0ea0f3e387f0501ab5c525be84ed6fbaa586dfc74': (2,'',[3,3],[3]),
 '27cded7a3d547326f6ae59662f81f3b9e69cb92275eecc4e790296f23818f238': (27,'',[4,4],[4]),
 '5cb496850ec0975632cb280398e183da9f67846efc666ab55d1a50d385690cf9': (6,'a',[2,2],[2]),
 '0b9d2c7e0da72ec6436c6544c3db5fb2a0833c5f2a00ce1c21e219d9c26b135a': (5,'',[4],[]),
 '6b9b622144d85c58c0449b391db24773bb4975f9f4a47ea8f9562662e675a1b2': (2,'a',[2,2],[2]),
 '0d93ea5567de9f59bdbb8cd65e7fc2244fb0c1c690aecd9beb453374f23644d2': (2,'',[4],[]),
}
SCHEME_FIXES = {'7dc2c3bfd024d7e32be2b3211c9e79b3cf757039b5c325b0270a08d2fbf065ea': (2,[],[2])}
# Four specific papers whose sequential text parser lost or misassigned question headings.
REBUILD = {'7b585c96ae0fd91cddedc683a73ee7475c9dcce30bfb05b963b8e56c501652fb','fb0f847af695e4baba940030bdcf9d8e3f1fbaacf6e0abdca3db62a827dda96a','3404449607f9003303dc09ae963f80ebd12410e2ece4c46238fb8a6dbe05d2e5','dbf0e6aef700d6759374fc6f15ec4cef7fe76ec18011f67ad8d1b5b9b1a8cb00'}
ONES='zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS='zero ten twenty thirty forty fifty sixty seventy eighty ninety'.split()


def count_cover(text):
    m=re.search(r'answer all ([a-z -]+?) questions',' '.join(text.lower().split()))
    if not m: return None
    w=m[1].replace('-',' ').split()
    if len(w)==1 and w[0] in ONES: return ONES.index(w[0])
    if len(w)==1 and w[0] in TENS: return TENS.index(w[0])*10
    if len(w)==2 and w[0] in TENS and w[1] in ONES[:10]: return TENS.index(w[0])*10+ONES.index(w[1])
    return None


def load_pdf(db,z,sha):
    for row in db.execute('SELECT path FROM files WHERE sha=? AND manifest_match=1 ORDER BY path',(sha,)):
        path=row[0]
        if path not in z.NameToInfo or z.getinfo(path).file_size>32*1024*1024: continue
        data=z.read(path)
        if hashlib.sha256(data).hexdigest()==sha: return fitz.open(stream=data,filetype='pdf')
    raise ValueError('Source absent or SHA-256 mismatch')


def lines(page):
    for block in page.get_text('dict')['blocks']:
        if block['type']!=0: continue
        for line in block['lines']:
            spans=[s for s in line['spans'] if s['text'].strip()]
            if spans: yield line['bbox'],''.join(s['text'] for s in spans).strip(),bool(spans[0]['flags']&16),spans[0]['font'],spans


def extract(doc,scheme=False,limit=None):
    n=0; part=letter=''; records={}; heads={}; totals=collections.defaultdict(list); warnings=[]
    for page_no,page in enumerate(doc,1):
        if page_no<=2: continue
        events=[]
        for (x,y,x1,y1),text,bold,font,spans in lines(page):
            if not (25<y<page.rect.height-(32 if scheme else 100)): continue
            if not scheme and re.search(r'for examiner[’\']?s use only',text,re.I): continue
            m=re.match(r'^([1-9]\d?)(?=\s|\(|$)',text)
            if not m and scheme and bold and 32<x<52: m=re.match(r'^([1-9]\d?)$',spans[0]['text'].strip())
            if m and bold and ('Times' in font or 'Arial' in font) and ((scheme and 32<x<52) or (not scheme and 45<x<76)):
                events.append((round(y,1),0,'q',int(m[1]))); text=text[m.end():].strip(); x+=20
            a=re.match(r'^\(([a-h])\)',text); r=re.match(r'^\((i{1,3}|iv|v|vi{1,3})\)',text)
            if bold and ((scheme and 50<x<125) or (not scheme and 73<x<125)):
                if a:
                    events.append((round(y,1),1,'p',a[1])); text=text[a.end():].strip(); r=re.match(r'^\((i{1,3}|iv|v|vi{1,3})\)',text)
                if r: events.append((round(y,1),2,'r',r[1]))
            if scheme:
                # Fraction answers can place the total's baseline just above the heading.
                if not bold and x>page.rect.width*.84 and re.fullmatch(r'\d{1,2}',text): events.append((round(y+2.5,1),4,'m',int(text)))
                codes=re.findall(r'(?<![A-Z])(?:MA|M|A|B)\d+\b',text)
                if codes: events.append((round(y,1),3,'c',codes))
            elif x1>page.rect.width*.80:
                for val in re.findall(r'\[(\d{1,2})\]',text): events.append((round(y,1),4,'m',int(val)))
        seen=set()
        for y,priority,kind,value in sorted(events,key=lambda e:(e[0],e[1])):
            key=(y,kind,str(value))
            if key in seen: continue
            seen.add(key)
            if kind=='q':
                if value==n+1 and (limit is None or value<=limit):
                    n=value; letter=part=''; heads[n]=page_no; records.setdefault((n,''),dict(page=page_no,end_page=page_no,marks=[],codes=[]))
                elif n and value!=n and (limit is None or n<limit): warnings.append((page_no,n,value))
            elif not n: continue
            elif kind in ('p','r'):
                if kind=='p': letter=part=value
                elif letter: part=letter+'.'+value
                records.setdefault((n,part),dict(page=page_no,end_page=page_no,marks=[],codes=[]))
            else:
                rec=records.setdefault((n,part),dict(page=page_no,end_page=page_no,marks=[],codes=[])); rec['end_page']=page_no
                if kind=='m':
                    if scheme: totals[n].append(value)
                    else: rec['marks'].append(value)
                else: rec['codes'].extend(value)
    return heads,records,totals,warnings


def corrected(raw,old,new):
    if raw!=old: raise ValueError('Source-specific correction no longer matches extracted evidence')
    return list(new)


def safe_undated(db,pair):
    if pair['year']!=2021 or pair['series']!='Summer' or pair['status']!='review' or not pair['paper'] or not pair['scheme']: return False
    p,s=[db.execute('SELECT * FROM documents WHERE sha=?',(pair[k],)).fetchone() for k in ('paper','scheme')]
    return all(x['issue']=='Series/date not established by cover' and x['exam_date'] is None for x in (p,s)) and all(p[k] and p[k]==s[k] for k in ('unit','component','code','print_id','tier','calculator','language'))


def reconcile(db,z):
    db.executescript('''CREATE TABLE IF NOT EXISTS structure_pairs(paper TEXT PRIMARY KEY REFERENCES documents,scheme TEXT NOT NULL REFERENCES documents,cover_questions INTEGER,question_count INTEGER,scheme_count INTEGER,paper_marks INTEGER,scheme_marks INTEGER,cover_marks INTEGER,status TEXT NOT NULL,date_state TEXT NOT NULL,detail TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS structure_questions(paper TEXT NOT NULL REFERENCES documents,num INTEGER NOT NULL,scheme TEXT NOT NULL REFERENCES documents,paper_page INTEGER NOT NULL,end_page INTEGER NOT NULL,scheme_page INTEGER,paper_marks INTEGER,scheme_marks INTEGER,parts TEXT NOT NULL,status TEXT NOT NULL,PRIMARY KEY(paper,num));''')
    report=[]
    for pair in db.execute("SELECT * FROM pairs WHERE paper IS NOT NULL AND scheme IS NOT NULL ORDER BY unit,year,series,component").fetchall():
        dated=pair['status']=='paired'; undated=safe_undated(db,pair)
        if not dated and not undated: continue
        paper,scheme=pair['paper'],pair['scheme']; detail=[]
        with load_pdf(db,z,paper) as p,load_pdf(db,z,scheme) as s:
            limit=count_cover(p[0].get_text()); ph,pr,_,pw=extract(p,limit=limit); sh,sr,st,sw=extract(s,True,limit)
        if paper in PAPER_FIXES:
            q,part,old,new=PAPER_FIXES[paper]; pr[q,part]['marks']=corrected(pr[q,part]['marks'],old,new); detail.append('Rendered-paper mark correction Q'+str(q)+part)
        if scheme in SCHEME_FIXES:
            q,old,new=SCHEME_FIXES[scheme]; st[q]=corrected(st.get(q,[]),old,new); detail.append('Rendered-scheme total correction Q'+str(q))
        pm=collections.Counter()
        for (q,part),rec in pr.items(): pm[q]+=sum(rec['marks'])
        sm={q:sum(v) for q,v in st.items()}; cover=db.execute('SELECT total_marks FROM documents WHERE sha=?',(paper,)).fetchone()[0]
        good=bool(limit and len(ph)==len(sh)==limit and set(pm)==set(sm)==set(ph) and all(pm[q]>0 and pm[q]==sm[q] for q in ph) and sum(pm.values())==sum(sm.values())==cover)
        if pw or sw: detail.append('Non-sequential extra heading candidates: '+str(len(pw)+len(sw)))
        if not good: detail.append('Question count/mark totals require review')
        if undated: detail.append('Matching component and print ID; 2021 series attributed to supplied archive; date not established')
        date_state='cover-confirmed' if dated else 'archive-attributed-date-unverified'
        with db:
            db.execute('DELETE FROM structure_questions WHERE paper=?',(paper,))
            db.execute('INSERT OR REPLACE INTO structure_pairs VALUES(?,?,?,?,?,?,?,?,?,?,?)',(paper,scheme,limit,len(ph),len(sh),sum(pm.values()),sum(sm.values()),cover,'reconciled' if good else 'review',date_state,json.dumps(detail)))
            for q,page in ph.items():
                parts=[]
                for (number,part),r in pr.items():
                    if number!=q: continue
                    ss=sr.get((q,part),{})
                    parts.append(dict(part=part,page=r['page'],end_page=r['end_page'],marks=sum(r['marks']) or None,scheme_page=ss.get('page'),codes=ss.get('codes',[])))
                end=max(x['end_page'] for x in parts)
                db.execute('INSERT INTO structure_questions VALUES(?,?,?,?,?,?,?,?,?,?)',(paper,q,scheme,page,end,sh.get(q),pm[q],sm.get(q),json.dumps(parts),'mark-total-agrees' if pm[q]>0 and pm[q]==sm.get(q) else 'review'))
            # Repair only the four explicitly identified broken paper structures, if no reviews exist.
            if good and dated and paper in REBUILD and db.execute('SELECT extracted_version FROM documents WHERE sha=?',(paper,)).fetchone()[0]!=5:
                reviewed=db.execute("SELECT 1 FROM questions q WHERE q.paper=? AND (q.verified_by IS NOT NULL OR q.status<>'review' OR EXISTS(SELECT 1 FROM reviews WHERE question_id=q.id))",(paper,)).fetchone()
                if not reviewed:
                    db.execute('DELETE FROM questions WHERE paper=?',(paper,))
                    for (q,part),r in pr.items():
                        ss=sr.get((q,part),{})
                        db.execute('INSERT INTO questions(paper,num,part,page,end_page,marks,scheme,scheme_page,codes,extraction_note) VALUES(?,?,?,?,?,?,?,?,?,?)',(paper,q,part,r['page'],r['end_page'],sum(r['marks']) or None,scheme,ss.get('page'),json.dumps(ss.get('codes',[])),'Coordinate-rebuilt candidate; question total reconciled, part/diagram/rubric review required'))
                    db.execute('UPDATE documents SET extracted_version=5,extracted_at=CURRENT_TIMESTAMP WHERE sha=? AND coalesce(extracted_version,0)<>5',(paper,))
            # Restore factual mark labels only on untouched candidate rows and only after all totals agree.
            if good and dated and paper in PAPER_FIXES:
                q,part,old,new=PAPER_FIXES[paper]
                db.execute("UPDATE questions SET marks=?,extraction_note='Rendered mark-label correction; source review still required' WHERE paper=? AND num=? AND part=? AND marks=? AND status='review' AND verified_by IS NULL AND NOT EXISTS(SELECT 1 FROM reviews WHERE question_id=questions.id)",(sum(new) or None,paper,q,part,sum(old)))
            # A tick glyph is extracted as [4] in this exact M5 paper; the rendered Q1 confirms no mark here.
            if good and dated and paper=='0b9d2c7e0da72ec6436c6544c3db5fb2a0833c5f2a00ce1c21e219d9c26b135a':
                db.execute("UPDATE questions SET marks=NULL,extraction_note='Rendered tick glyph is not a mark label; source review still required' WHERE paper=? AND num=1 AND part='' AND marks=4 AND status='review' AND verified_by IS NULL AND NOT EXISTS(SELECT 1 FROM reviews WHERE question_id=questions.id)",(paper,))
        report.append(dict(unit=pair['unit'],year=pair['year'],series=pair['series'],component=pair['component'],paper=paper,scheme=scheme,date_state=date_state,questions=len(ph),scheme_questions=len(sh),cover_questions=limit,paper_marks=sum(pm.values()),scheme_marks=sum(sm.values()),cover_marks=cover,matched_questions=sum(pm[q]>0 and pm[q]==sm.get(q) for q in ph),status='reconciled' if good else 'review',detail='; '.join(detail)))
    return report


def refresh(db):
    summary=json.loads(db.execute('SELECT summary FROM state WHERE id=1').fetchone()[0])
    for row in summary:
        u=row['unit']; stats=db.execute('''SELECT count(*),count(q.skill),count(DISTINCT q.skill),count(DISTINCT p.qid),count(DISTINCT CASE WHEN p.qid IS NOT NULL THEN q.skill END) FROM questions q JOIN documents d ON d.sha=q.paper LEFT JOIN postings p ON p.qid=q.id AND p.unit=d.unit AND p.term='*' WHERE d.unit=?''',(u,)).fetchone()
        row.update(questions=stats[0],classified=stats[1],candidate_skills=stats[2],verified=stats[3],covered_skills=stats[4],review=stats[0]-stats[3],last_extraction=db.execute('SELECT max(extracted_at) FROM documents WHERE unit=? AND extracted_version>0',(u,)).fetchone()[0])
    db.execute('UPDATE state SET revision=revision+1,summary=? WHERE id=1',(json.dumps(summary),))


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--db',required=True); p.add_argument('--archive',required=True); p.add_argument('--out',required=True); a=p.parse_args()
    if not Path(a.db).is_file(): raise FileNotFoundError(a.db)
    db=sqlite3.connect(a.db); db.row_factory=sqlite3.Row; db.execute('PRAGMA foreign_keys=ON')
    try:
        with zipfile.ZipFile(a.archive) as z: report=reconcile(db,z)
        with db:
            refresh(db)
            for u in ('M1','M2','M5','M6'):
                rows=[r for r in report if r['unit']==u]
                db.execute('INSERT INTO runs(unit,phase,detail) VALUES(?,?,?)',(u,'coordinate-reconciliation-v1',json.dumps({'pairs':len(rows),'reconciled':sum(r['status']=='reconciled' for r in rows)})))
        out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
        for name,rows in [('coordinate-pairs.csv',report),('coordinate-questions.csv',[dict(r) for r in db.execute('SELECT d.unit,d.year,d.series,d.component,q.* FROM structure_questions q JOIN documents d ON d.sha=q.paper ORDER BY d.unit,d.year,d.series,d.component,q.num')])]:
            with (out/name).open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        print(json.dumps(dict(pairs=len(report),reconciled=sum(r['status']=='reconciled' for r in report),dated_reconciled=sum(r['status']=='reconciled' and r['date_state']=='cover-confirmed' for r in report),question_totals=sum(r['questions'] for r in report),matched_questions=sum(r['matched_questions'] for r in report)),indent=2))
    finally: db.close()

if __name__=='__main__': main()
