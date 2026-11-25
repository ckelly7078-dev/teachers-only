"""Offline, unit-scoped importer. All PDF text is transient."""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

from .db import UNITS, connect, index_question, refresh, tokens

VERSION = 1
EXTRACTION_VERSION = 3
KINDS = {'Question paper':'paper', 'Mark scheme':'scheme'}
MONTHS = {'MAY':'Summer','JUNE':'Summer','NOVEMBER':'November','JANUARY':'January'}
MAX_PDF = 32 * 1024 * 1024


def digest(path):
    with Path(path).open('rb') as src:
        return hashlib.file_digest(src, 'sha256').hexdigest()


def rows(z, path):
    with z.open(path) as src:
        return list(csv.DictReader(io.TextIOWrapper(src, encoding='utf-8-sig', newline='')))


def pdf_pages(data, cover=False):
    args = ['pdftotext','-layout','-enc','UTF-8']
    if cover:
        args += ['-f','1','-l','1']
    run = subprocess.run(args+['-','-'],input=data,capture_output=True,timeout=45,check=True)
    return run.stdout.decode('utf-8').rstrip('\f').split('\f')


def capture(pattern, value):
    result = re.search(pattern,value,re.I)
    return result.group(1) if result else None


def cover_fields(data, unit, year, series, component, kind):
    if not data.startswith(b'%PDF-'):
        raise ValueError('Invalid PDF signature')
    cover = ' '.join(pdf_pages(data,True)[0].split())
    info = subprocess.run(['pdfinfo','-'],input=data,capture_output=True,timeout=20,check=True)
    pages = int(capture(r'Pages:\s*(\d+)',info.stdout.decode(errors='replace')))
    codes = set(re.findall(r'\bGMC\d{2}\b',cover,re.I))
    code = next(iter(codes)).upper() if len(codes)==1 else None
    ids = set(re.findall(r'(?<![\w.])(\d{5})(?!\d)',cover))
    print_id = next(iter(ids)) if len(ids)==1 else None
    date = re.search(r'\b(\d{1,2})\s+(MAY|JUNE|JANUARY|NOVEMBER|DECEMBER)\b',cover,re.I)
    observed_year = capture(r'\b(20\d{2})\b',cover)
    exam_date = f'{observed_year} {date[2].upper()} {int(date[1])}' if date and observed_year else None
    expected_code = 'GMC'+unit[-1]+('2' if component=='Paper 2' else '1')
    scheme = bool(re.search(r'MARK\s+SCHEME',cover,re.I))
    tier = 'Foundation' if re.search(r'Foundation\s+Tier',cover,re.I) else None
    calc = ('non-calculator' if re.search(r'non[\s-]*calculator|must not use a calculator',cover,re.I)
            else 'calculator' if 'calculator' in cover.lower() else None)
    duration = re.search(r'TIME\s+(\d+)\s+hours?(?:\s+(\d+)\s+minutes?)?',cover,re.I)
    marks = capture(r'total mark for this paper is\s+(\d+)',cover)
    issues = []
    if code != expected_code or not tier or scheme != (kind=='scheme') or not print_id or not calc:
        issues.append('Cover identity/type/tier/calculator/print code needs review')
    session = capture(r'\b(January|November)\s+20\d{2}\b',cover)
    cover_series = session.title() if session else (MONTHS.get(date[2].upper()) if date else None)
    if not exam_date or observed_year!=str(year) or cover_series!=series:
        issues.append('Series/date not established by cover')
    return dict(tier=tier,language='English' if 'mathematics' in cover.lower() and tier else None,
                code=code,print_id=print_id,exam_date=exam_date,pages=pages,calculator=calc,
                duration_min=60*int(duration[1])+int(duration[2] or 0) if duration else None,
                total_marks=int(marks) if marks else None,cover_status='review' if issues else 'checked',
                issue=' | '.join(issues) or None)


def descriptor(row):
    return (row['Unit'],int(row['Year']),row['Series'],row['Component'],KINDS[row['Document type']])


def pair_unit(db,unit):
    before = {tuple(r) for r in db.execute('SELECT * FROM pairs WHERE unit=?',(unit,))}
    db.execute('DELETE FROM pairs WHERE unit=?',(unit,))
    for key in db.execute('SELECT DISTINCT unit,year,series,component FROM expected WHERE unit=?',(unit,)).fetchall():
        files = db.execute("""SELECT d.*,f.kind declared_kind,min(f.manifest_match) manifest_match
          FROM files f JOIN documents d ON f.sha=d.sha
          WHERE (f.unit,f.year,f.series,f.component)=(?,?,?,?) GROUP BY f.sha,f.kind""",tuple(key)).fetchall()
        papers = [r for r in files if r['declared_kind']=='paper']
        schemes = [r for r in files if r['declared_kind']=='scheme']
        p = papers[0] if len(papers)==1 else None
        s = schemes[0] if len(schemes)==1 else None
        if not papers or not schemes:
            status, reason = 'missing','Component absent from supplied inventory'
        elif not p or not s:
            status, reason = 'review','Multiple distinct files claim the same component'
        elif (all(r['cover_status']=='checked' and r['manifest_match']==1 and
                  tuple(r[k] for k in ('unit','year','series','component'))==tuple(key) and
                  r['declared_kind']==r['kind'] for r in (p,s))
              and all(p[k] and p[k]==s[k] for k in ('code','exam_date','print_id','calculator'))):
            status, reason = 'paired','Both covers agree on component, date, print identifier and calculator'
        else:
            status, reason = 'review','Unconfirmed cover date, identity or conflicting document evidence'
        db.execute('INSERT INTO pairs VALUES(?,?,?,?,?,?,?,?)',
                   (*key,p['sha'] if p else None,s['sha'] if s else None,status,reason))
    after = {tuple(r) for r in db.execute('SELECT * FROM pairs WHERE unit=?',(unit,))}
    if before!=after:
        for row in db.execute("""SELECT q.id FROM questions q JOIN documents d ON d.sha=q.paper
                                 WHERE d.unit=? AND q.status='verified'""",(unit,)).fetchall():
            index_question(db,row[0])


def audit(db,z,unit,archive_sha):
    manifest = rows(z,'00_INVENTORY.csv')
    paths = [r['Archive path'] for r in manifest]
    actual = [n for n in z.namelist() if n.lower().endswith('.pdf')]
    if sorted(actual)!=sorted(paths) or len(set(actual))!=len(actual):
        raise ValueError('Manifest membership differs from the archive, or a path repeats')
    missing = rows(z,'00_MISSING_DOCUMENTS.csv')
    subset = [r for r in manifest if r['Unit']==unit]
    done = skipped = 0
    for r in subset:
        path = r['Archive path']
        if not path.startswith(unit+'/') or z.getinfo(path).file_size>MAX_PDF:
            raise ValueError('Invalid source path or excessive PDF size')
        if db.execute('SELECT 1 FROM audited WHERE archive_sha=? AND path=? AND parser=?',
                      (archive_sha,path,VERSION)).fetchone():
            skipped += 1
            continue
        data = z.read(path)
        sha = hashlib.sha256(data).hexdigest()
        key = descriptor(r)
        with db:
            prior = db.execute('SELECT sha FROM files WHERE path=?',(path,)).fetchone()
            if prior and prior[0]!=sha:
                raise ValueError('Source changed at existing path. Retain it under a new versioned path for pairing review.')
            if not db.execute("SELECT 1 FROM documents WHERE sha=? AND cover_status!='error'",(sha,)).fetchone():
                try:
                    fields = cover_fields(data,*key)
                except (ValueError,TypeError,subprocess.SubprocessError) as exc:
                    fields = dict(cover_status='error',issue=type(exc).__name__)
                cols = list(fields)
                db.execute(f"""INSERT INTO documents (sha,unit,year,series,component,kind,{','.join(cols)})
                    VALUES ({','.join('?' for _ in range(6+len(cols)))})
                    ON CONFLICT(sha) DO UPDATE SET {','.join(c+'=excluded.'+c for c in cols)}""",
                           (sha,*key,*fields.values()))
            match = int(sha==r['SHA256'].lower() and len(data)==int(r['Bytes']))
            db.execute('INSERT OR REPLACE INTO files VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                       (path,sha,len(data),r['SHA256'],r['Source'],match,*key))
            if match and db.execute('SELECT cover_status FROM documents WHERE sha=?',(sha,)).fetchone()[0]!='error':
                db.execute('INSERT OR IGNORE INTO audited VALUES(?,?,?)',(archive_sha,path,VERSION))
        done+=1
    with db:
        db.executemany('INSERT OR IGNORE INTO expected VALUES(?,?,?,?,?)',
                       (descriptor(r) for r in subset+missing if r['Unit']==unit))
        pair_unit(db,unit)
        db.execute('INSERT INTO runs(unit,phase,detail) VALUES(?,?,?)',(unit,'audit',json.dumps(dict(read=done,skipped=skipped))))
        refresh(db)
    return dict(read=done,skipped=skipped)


HEAD = re.compile(r'^\s{0,12}([1-9]\d?)(?:\s+(\S.*))?\s*$')
PART = re.compile(r'^\(([a-h])\)\s*')
ROMAN = re.compile(r'^\((i{1,3}|iv|v|vi{1,3})\)\s*')
CODE = re.compile(r'(?<![A-Z])(MA|M|A|B)(\d+)\b')


def anchors(pages,scheme=False):
    """Candidate page anchors and numeric evidence only. Layout uncertainty remains reviewable."""
    records = {}
    number = 0
    letter = part = ''
    for page,lineblock in enumerate(pages,1):
        if page < 2:
            continue
        for line in lineblock.splitlines():
            m = HEAD.match(line)
            text = line.strip()
            if m and int(m[1])==number+1:
                number += 1
                text = (m[2] or '').lstrip()
                part = letter = ''
            elif not number:
                continue
            sub = PART.match(text)
            if sub:
                letter = part = sub[1]
                text = text[sub.end():]
            roman = ROMAN.match(text.strip())
            if roman and letter:
                part = letter+'.'+roman[1]
            key = (number,part)
            marks = [int(x) for x in re.findall(r'\[(\d{1,2})\]',text)]
            codes = [kind+n for kind,n in CODE.findall(text)]
            if (m and int(m[1])==number) or sub or roman or (codes if scheme else marks):
                r = records.setdefault(key,dict(page=page,end_page=page,marks=[],codes=[]))
                r['end_page']=page
                r['marks'].extend(marks)
                r['codes'].extend(codes)
            if key in records and not scheme:
                records[key].setdefault('words',set()).update(tokens(text))
    return records


def suggest(words,skills):
    # Distinctive matches only. A tie or an ambiguous generic term leaves the field open.
    generic = {'the','of','and','a','an','to','as','amount','quantity','number','numbers',
               'value','measurement','line','data','table','use','from','correct','one'}
    scores = sorted(((len((words-generic) & terms),name) for name,terms in skills),reverse=True)
    if scores and scores[0][0]>=2 and (len(scores)==1 or scores[0][0]>scores[1][0]):
        return scores[0][1]
    return None


def extract(db,z,unit):
    done = skipped = failures = 0
    skills = [(r['id'],set(tokens(r['terms']+' '+r['label']))) for r in
              db.execute('SELECT * FROM skills WHERE unit=?',(unit,))]
    pairs = db.execute("SELECT * FROM pairs WHERE unit=? AND status='paired' ORDER BY year,series",(unit,)).fetchall()
    for pair in pairs:
        paper,scheme = pair['paper'],pair['scheme']
        def load_pdf(sha):
            matches = db.execute('SELECT path FROM files WHERE sha=? ORDER BY path',(sha,))
            for row in matches:
                if row[0] in z.NameToInfo:
                    data = z.read(row[0])
                    if hashlib.sha256(data).hexdigest()==sha:
                        return data
            raise ValueError('Audit source archive before extraction')
        doc = db.execute('SELECT extracted_version FROM documents WHERE sha=?',(paper,)).fetchone()
        if doc[0]==EXTRACTION_VERSION and db.execute('SELECT 1 FROM questions WHERE paper=? AND scheme=? LIMIT 1',(paper,scheme)).fetchone():
            skipped+=1
            continue
        try:
            pins = anchors(pdf_pages(load_pdf(paper)))
            scheme_pins = anchors(pdf_pages(load_pdf(scheme)),True)
            declared = db.execute('SELECT total_marks FROM documents WHERE sha=?',(paper,)).fetchone()[0]
            candidate_total = sum(sum(r['marks']) for r in pins.values())
            issue = None if candidate_total==declared else f'Candidate marks sum to {candidate_total}; cover states {declared}'
            if not pins or not scheme_pins:
                raise ValueError('No question anchors on paper or scheme')
            with db:
                for previous in db.execute("SELECT id,num,part FROM questions WHERE paper=? AND status='review'",(paper,)).fetchall():
                    if (previous['num'],previous['part']) not in pins:
                        db.execute("DELETE FROM questions WHERE id=? AND NOT EXISTS (SELECT 1 FROM reviews WHERE question_id=?)",
                                   (previous['id'],previous['id']))
                for (num,part),r in pins.items():
                    s = scheme_pins.get((num,part),{})
                    db.execute("""INSERT INTO questions(paper,num,part,page,end_page,marks,scheme,scheme_page,codes)
                        VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(paper,num,part) DO UPDATE SET
                        page=excluded.page,end_page=excluded.end_page,marks=excluded.marks,scheme=excluded.scheme,
                        scheme_page=excluded.scheme_page,codes=excluded.codes WHERE questions.status='review'""",
                        (paper,num,part,r['page'],r['end_page'],sum(r['marks']) or None,scheme,
                         s.get('page'),json.dumps(s.get('codes',[]))))
                    words = r.get('words',set()) | pins.get((num,''),{}).get('words',set())
                    db.execute("""UPDATE questions SET skill=? WHERE paper=? AND num=? AND part=?
                        AND status='review' AND verified_by IS NULL""",(suggest(words,skills),paper,num,part))
                db.execute("""UPDATE documents SET extracted_version=?,extracted_at=CURRENT_TIMESTAMP
                              WHERE sha IN (?,?)""",(EXTRACTION_VERSION,paper,scheme))
                db.execute("UPDATE questions SET extraction_note=? WHERE paper=? AND status='review'",(issue,paper))
            done+=1
        except (ValueError,subprocess.SubprocessError) as exc:
            with db:
                db.execute('UPDATE documents SET extracted_version=-1 WHERE sha=?',(paper,))
                db.execute('INSERT INTO runs(unit,phase,detail) VALUES(?,?,?)',(unit,'error',f'{paper}: {exc}'))
            failures+=1
    with db:
        refresh(db)
    return dict(extracted_pairs=done,skipped_pairs=skipped,failures=failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['audit','extract'])
    parser.add_argument('--db',required=True)
    parser.add_argument('--archive',required=True)
    parser.add_argument('--unit',required=True,choices=UNITS)
    args = parser.parse_args()
    db = connect(args.db,True)
    try:
        with zipfile.ZipFile(args.archive) as z:
            result = (audit(db,z,args.unit,digest(args.archive)) if args.phase=='audit'
                      else extract(db,z,args.unit))
        print(json.dumps(result))
        if result.get('failures'):
            raise SystemExit(1)
    finally:
        db.close()


if __name__=='__main__':
    main()
