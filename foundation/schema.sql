PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS state(
 id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, identity TEXT NOT NULL,
 summary TEXT NOT NULL DEFAULT '[]'
);
INSERT OR IGNORE INTO state(id,revision,identity) VALUES (1,0,hex(randomblob(16)));
CREATE TABLE IF NOT EXISTS documents(
 sha TEXT PRIMARY KEY, unit TEXT NOT NULL CHECK(unit IN ('M1','M2','M5','M6')),
 year INTEGER NOT NULL, series TEXT NOT NULL, component TEXT NOT NULL, kind TEXT NOT NULL,
 board TEXT NOT NULL DEFAULT 'CCEA', qualification TEXT NOT NULL DEFAULT 'GCSE Mathematics',
 specification TEXT NOT NULL DEFAULT '2017 (archive attribution)', tier TEXT, calculator TEXT,
 language TEXT, official_url TEXT, code TEXT, print_id TEXT, exam_date TEXT, pages INTEGER,
 total_marks INTEGER, duration_min INTEGER, cover_status TEXT NOT NULL, issue TEXT,
 extracted_version INTEGER, extracted_at TEXT
);
CREATE INDEX IF NOT EXISTS component_lookup ON documents(unit,year,series,component,kind);
CREATE TABLE IF NOT EXISTS files(
 path TEXT PRIMARY KEY, sha TEXT NOT NULL REFERENCES documents, bytes INTEGER NOT NULL,
 manifest_sha TEXT, declared_source TEXT, manifest_match INTEGER NOT NULL, unit TEXT NOT NULL,
 year INTEGER NOT NULL, series TEXT NOT NULL, component TEXT NOT NULL, kind TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS expected(
 unit TEXT, year INTEGER, series TEXT, component TEXT, kind TEXT,
 PRIMARY KEY(unit,year,series,component,kind)
);
CREATE TABLE IF NOT EXISTS pairs(
 unit TEXT, year INTEGER, series TEXT, component TEXT, paper TEXT REFERENCES documents,
 scheme TEXT REFERENCES documents, status TEXT, reason TEXT,
 PRIMARY KEY(unit,year,series,component)
);
CREATE TABLE IF NOT EXISTS skills(
 id TEXT PRIMARY KEY, unit TEXT NOT NULL, strand TEXT NOT NULL, label TEXT NOT NULL,
 page INTEGER NOT NULL, terms TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS questions(
 id INTEGER PRIMARY KEY, paper TEXT NOT NULL REFERENCES documents, num INTEGER NOT NULL,
 part TEXT NOT NULL DEFAULT '', page INTEGER NOT NULL, end_page INTEGER NOT NULL,
 marks INTEGER, scheme TEXT REFERENCES documents, scheme_page INTEGER, codes TEXT,
 extraction_note TEXT, skill TEXT REFERENCES skills, annotation TEXT, answer TEXT, rules TEXT,
 status TEXT NOT NULL DEFAULT 'review', verified_by TEXT, depends_on TEXT,
 UNIQUE(paper,num,part)
);
CREATE INDEX IF NOT EXISTS question_review ON questions(status,id);
CREATE TABLE IF NOT EXISTS postings(
 unit TEXT NOT NULL, term TEXT NOT NULL, qid INTEGER NOT NULL REFERENCES questions ON DELETE CASCADE,
 PRIMARY KEY(unit,term,qid)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS reviews(
 id INTEGER PRIMARY KEY, question_id INTEGER NOT NULL REFERENCES questions, actor TEXT NOT NULL,
 at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, before_json TEXT NOT NULL, after_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs(
 id INTEGER PRIMARY KEY, unit TEXT NOT NULL, at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 phase TEXT NOT NULL, detail TEXT NOT NULL
);
PRAGMA user_version=1;
CREATE TABLE IF NOT EXISTS audited(
 archive_sha TEXT, path TEXT, parser INTEGER, PRIMARY KEY(archive_sha,path,parser)
);
CREATE INDEX IF NOT EXISTS paper_questions ON questions(paper,id);
CREATE TABLE IF NOT EXISTS practice_drafts(
 id INTEGER PRIMARY KEY, owner TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'draft',
 data TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, approved TEXT
);
CREATE INDEX IF NOT EXISTS teacher_drafts ON practice_drafts(owner,id);
CREATE INDEX IF NOT EXISTS review_history ON reviews(question_id,id);
