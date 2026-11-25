"""Offline Foundation examiner report anchor ingestion; no verbatim text retained."""
import argparse, csv, hashlib, json, re, sqlite3
from pathlib import Path
import fitz

HEAD = re.compile(r'^\s*Assessment Unit\s+M?([1-8])([12])?\s+(Foundation|Higher) Tier(?:\s+(Non-Calculator|Calculator))?', re.I)
COVER = re.compile(r'(Summer|January|November)\s+Series\s+(20\d{2})', re.I)
Q = re.compile(r'Q\s*(\d{1,2})\b')
SCHEMA = '''
CREATE TABLE IF NOT EXISTS examiner_reports(sha TEXT PRIMARY KEY, filename TEXT NOT NULL, year INTEGER NOT NULL, series TEXT NOT NULL, pages INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS examiner_sections(report_sha TEXT REFERENCES examiner_reports,unit TEXT,component TEXT,start_page INTEGER,end_page INTEGER,paper TEXT REFERENCES documents,status TEXT,PRIMARY KEY(report_sha,unit,component));
CREATE TABLE IF NOT EXISTS examiner_anchors(report_sha TEXT,unit TEXT,component TEXT,num INTEGER,start_page INTEGER,end_page INTEGER,paper TEXT REFERENCES documents,status TEXT NOT NULL,PRIMARY KEY(report_sha,unit,component,num),FOREIGN KEY(report_sha,unit,component) REFERENCES examiner_sections);
CREATE TABLE IF NOT EXISTS examiner_notes(report_sha TEXT,unit TEXT,component TEXT,num INTEGER,topic TEXT,note TEXT,review_status TEXT NOT NULL,PRIMARY KEY(report_sha,unit,component,num,topic),FOREIGN KEY(report_sha,unit,component,num) REFERENCES examiner_anchors);
'''

def parse(path):
    with fitz.open(path) as doc:
        cover=' '.join(doc[0].get_text().split()); m=COVER.search(cover)
        if not m or 'Examiner' not in cover or 'Mathematics' not in cover: raise ValueError('Not a supported mathematics examiner report')
        sections=[]; active=None; count=len(doc)
        # First 6 pages are cover/front matter/contents for these reports.
        for page_idx in range(6,count):
            page=page_idx+1
            for line in doc[page_idx].get_text(sort=True).splitlines():
                h=HEAD.match(line)
                if h:
                    if active: active['end_page']=page
                    active=None
                    if h[3].lower()=='foundation' and h[1] in '1256':
                        comp='Single paper' if h[1] in '12' else {'non-calculator':'Paper 1','calculator':'Paper 2'}.get((h[4] or '').lower())
                        if not comp: raise ValueError('Unclear calculator component')
                        active=dict(unit='M'+h[1],component=comp,start_page=page,end_page=page,anchors=[]); sections.append(active)
                    continue
                if active:
                    if re.match(r'^\s*Contact details',line,re.I): active=None; continue
                    active['end_page']=page
                    for q in Q.finditer(line):
                        n=int(q[1]); prior=active['anchors']
                        # Reject out-of-order references, allowing gaps for review.
                        if n==1 and not prior or prior and n>prior[-1][0]:
                            if prior: prior[-1][2]=page
                            prior.append([n,page,page])
                    if active['anchors']: active['anchors'][-1][2]=page
        return m[1].title(),int(m[2]),count,sections

def ingest(db,path):
    series,year,count,sections=parse(path); sha=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    db.execute('INSERT OR IGNORE INTO examiner_reports VALUES(?,?,?,?,?)',(sha,Path(path).name,year,series,count))
    for s in sections:
        key=(sha,s['unit'],s['component']); pair=db.execute('SELECT paper,status FROM pairs WHERE unit=? AND year=? AND series=? AND component=?',(s['unit'],year,series,s['component'])).fetchone()
        paper=pair[0] if pair and pair[1]=='paired' else None
        expected={r[0] for r in db.execute('SELECT num FROM structure_questions WHERE paper=?',(paper,))} if paper else set()
        found={a[0] for a in s['anchors']}; status='linked' if paper and found==expected else 'review'
        db.execute('INSERT OR IGNORE INTO examiner_sections VALUES(?,?,?,?,?,?,?)',(*key,s['start_page'],s['end_page'],paper,status))
        for num,start,end in s['anchors']:
            db.execute('INSERT OR IGNORE INTO examiner_anchors VALUES(?,?,?,?,?,?,?,?)',(*key,num,start,end,paper if num in expected else None,'linked' if num in expected else 'review'))
    return sha

def export(db,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for table in ('examiner_reports','examiner_sections','examiner_anchors','examiner_notes'):
        q=db.execute('SELECT * FROM '+table+' ORDER BY 1,2,3');
        with (out/(table+'.csv')).open('w',encoding='utf8',newline='') as f:
            w=csv.writer(f);w.writerow(x[0] for x in q.description);w.writerows(q)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--out',required=True);p.add_argument('reports',nargs='+');a=p.parse_args()
    if not Path(a.db).is_file(): raise FileNotFoundError(a.db)
    with sqlite3.connect(a.db) as db:
        db.execute('PRAGMA foreign_keys=ON');db.executescript(SCHEMA)
        for path in a.reports: ingest(db,path)
        export(db,a.out)
        print(db.execute('SELECT count(*),sum(status="linked") FROM examiner_anchors').fetchone())
if __name__=='__main__': main()
