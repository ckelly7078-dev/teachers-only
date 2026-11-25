"""Persistent metadata and bounded, revision-aware retrieval."""
import csv
import json
import re
import sqlite3
from contextlib import contextmanager
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNITS = ('M1', 'M2', 'M5', 'M6')
SPEC = 'CCEA GCSE Mathematics (2017), version 2, section 3.1'


def connect(path, initialize=False):
    if not initialize and not Path(path).is_file():
        raise FileNotFoundError('Foundation database has not been provisioned')
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    if initialize:
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version not in (0, 1):
            raise ValueError('Unsupported schema version')
        db.execute('PRAGMA journal_mode=WAL')
        db.executescript((HERE / 'schema.sql').read_text())
        with (HERE / 'skills.tsv').open() as src, db:
            for r in csv.DictReader(src, delimiter='\t'):
                db.execute('INSERT OR IGNORE INTO skills VALUES(?,?,?,?,?,?)',
                           (r['id'], 'M1', r['strand'], r['label'], int(r['page']), r['terms']))
    return db


def tokens(value):
    return re.findall(r"[a-z0-9]+", value.lower())


def normalize(term):
    if term.endswith('ies') and len(term)>4:
        return term[:-3]+'y'
    if term.endswith('s') and len(term)>3 and not term.endswith(('ss','us')):
        return term[:-1]
    return term


def index_question(db, qid):
    db.execute('DELETE FROM postings WHERE qid=?', (qid,))
    record = db.execute("""SELECT d.unit, s.label, s.terms, q.annotation, s.id skill, d.year,
        d.series, d.calculator, q.marks FROM questions q JOIN skills s ON s.id=q.skill
        JOIN documents d ON d.sha=q.paper JOIN pairs p ON p.paper=q.paper AND p.scheme=q.scheme
        WHERE q.id=? AND q.status='verified' AND p.status='paired'""", (qid,)).fetchone()
    if record:
        terms = {normalize(t) for t in tokens(' '.join(str(x) for x in record))} | {'*', record['skill']}
        db.executemany('INSERT INTO postings VALUES(?,?,?)',
                       ((record['unit'], t, qid) for t in terms))


def refresh(db):
    summary = []
    for unit in UNITS:
        def count(sql):
            return db.execute(sql, (unit,)).fetchone()[0]
        qstats = db.execute("""SELECT count(*),count(q.skill),count(DISTINCT q.skill),
            count(DISTINCT r.qid),count(DISTINCT CASE WHEN r.qid IS NOT NULL THEN q.skill END) FROM questions q
            LEFT JOIN postings r ON r.qid=q.id AND r.unit=? AND r.term='*'
            JOIN documents d ON d.sha=q.paper WHERE d.unit=?""", (unit,unit)).fetchone()
        pair_counts = dict(db.execute('SELECT status,count(*) FROM pairs WHERE unit=? GROUP BY status', (unit,)))
        summary.append(dict(unit=unit, papers=count("SELECT count(*) FROM documents WHERE kind='paper' AND unit=?"),
            paired=pair_counts.get('paired',0), pair_review=pair_counts.get('review',0),
            missing=count("""SELECT count(*) FROM expected e WHERE unit=? AND NOT EXISTS
                (SELECT 1 FROM files f WHERE (f.unit,f.year,f.series,f.component,f.kind)=
                (e.unit,e.year,e.series,e.component,e.kind))"""),
            reports=count("SELECT count(*) FROM documents WHERE kind='report' AND unit=?"),
            questions=qstats[0], classified=qstats[1], covered_skills=qstats[4], candidate_skills=qstats[2],
            skills=count('SELECT count(*) FROM skills WHERE unit=?'), verified=qstats[3], review=qstats[0]-qstats[3],
            failures=count("SELECT count(*) FROM documents WHERE unit=? AND (cover_status='error' OR extracted_version=-1)"),
            last_extraction=count("SELECT max(extracted_at) FROM documents WHERE unit=? AND extracted_version>0")))
    db.execute('UPDATE state SET revision=revision+1,summary=? WHERE id=1', (json.dumps(summary),))


DETAIL = """SELECT q.*,d.unit,d.year,d.series,d.component,d.calculator,s.label,s.strand,s.page spec_page
    FROM questions q JOIN documents d ON d.sha=q.paper LEFT JOIN skills s ON s.id=q.skill"""


@lru_cache(maxsize=256)
def _search(path, identity, revision, unit, words, limit, skill):
    with connection(path) as db:
        scores = Counter()
        for word in words or (skill or '*',):
            rows = db.execute('SELECT qid FROM postings WHERE unit=? AND term=? ORDER BY qid DESC LIMIT 96',
                              (unit,word))
            scores.update(row[0] for row in rows)
        result = []
        for qid, _ in scores.most_common():
            row = db.execute(DETAIL+" WHERE q.id=? AND q.status='verified'", (qid,)).fetchone()
            if row and (not skill or row['skill']==skill):
                result.append(dict(row))
            if len(result)==limit:
                break
        return json.dumps(result, ensure_ascii=False)




@contextmanager
def connection(path):
    db = connect(path)
    try:
        yield db
    finally:
        db.close()


def search(path, unit, query='', limit=5, skill=''):
    if unit not in UNITS or not 1 <= limit <= 8 or len(query)>160:
        raise ValueError('Invalid unit, query length or result limit')
    with connection(path) as db:
        identity, revision = db.execute('SELECT identity,revision FROM state').fetchone()
    words = tuple(dict.fromkeys(normalize(t) for t in tokens(query)))[:8]
    return json.loads(_search(str(Path(path).resolve()), identity, revision, unit, words, limit, skill))
