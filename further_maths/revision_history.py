"""Offline question history migration and explicit version succession; no release approval."""
import hashlib
import json
from contextlib import contextmanager
from active_difficulty import SUCCESSIONS, require

COLUMNS=('question_id','old_payload','old_marks','old_status','old_sha256','revision')
HISTORY='difficulty_revision_history'

@contextmanager
def atomic(db):
    require(db.execute('pragma foreign_keys').fetchone()==(1,), 'Enable foreign keys before migration')
    db.execute('SAVEPOINT revision_history_operation')
    try:
        yield
    except BaseException:
        db.execute('ROLLBACK TO revision_history_operation')
        db.execute('RELEASE revision_history_operation')
        raise
    else:
        db.execute('RELEASE revision_history_operation')


def digest(payload):
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def verify_history(db):
    rows=db.execute('SELECT * FROM difficulty_revision_history').fetchall()
    require(all(digest(row[1])==row[4] for row in rows), 'Historical payload hash mismatch')
    require(len({(row[0],row[5]) for row in rows})==len(rows), 'Duplicate retirement revision')
    return len(rows)


def upgrade_history(db):
    """Replace legacy single-key table atomically, retaining all six original fields."""
    with atomic(db):
        columns=db.execute('PRAGMA table_info(difficulty_revision_history)').fetchall()
        require(tuple(x[1] for x in columns)==COLUMNS, 'Unknown history schema')
        keys=tuple(x[1] for x in sorted((x for x in columns if x[5]),key=lambda x:x[5]))
        require(keys in (('question_id',),('question_id','revision')), 'Unknown history primary key')
        count=verify_history(db)
        if keys==('question_id','revision'):
            return count
        require(db.execute("SELECT name FROM sqlite_master WHERE sql LIKE '%difficulty_revision_history%' AND name<>?",(HISTORY,)).fetchall()==[], 'Unexpected history dependency')
        old=db.execute('SELECT * FROM difficulty_revision_history ORDER BY question_id,revision').fetchall()
        db.execute('ALTER TABLE difficulty_revision_history RENAME TO difficulty_revision_history_legacy')
        db.execute('''CREATE TABLE difficulty_revision_history (
          question_id TEXT NOT NULL REFERENCES calibrated_pathway_questions(id),
          old_payload TEXT NOT NULL, old_marks INTEGER NOT NULL, old_status TEXT NOT NULL,
          old_sha256 TEXT NOT NULL, revision TEXT NOT NULL,
          PRIMARY KEY(question_id,revision))''')
        db.execute('INSERT INTO difficulty_revision_history SELECT * FROM difficulty_revision_history_legacy')
        require(db.execute('SELECT * FROM difficulty_revision_history ORDER BY question_id,revision').fetchall()==old, 'History copy differs')
        db.execute('DROP TABLE difficulty_revision_history_legacy')
        require(not db.execute('PRAGMA foreign_key_check').fetchall(),'Foreign key failure')
        return count


def replace_authorised(db,resolver,path,tier,variant,successor):
    """Archive the exact active predecessor then replace it, only for a declared succession."""
    predecessor=SUCCESSIONS.get((path,tier,successor))
    require(predecessor is not None,'Unauthorised succession')
    old=resolver._resolve_version(path,tier,variant,predecessor)
    new=resolver._resolve(path,tier,variant)
    require(new['revision']=='FM-16'+successor.upper(),'Successor is not active')
    require(old['marks']==new['marks'] and old['scope']==new['scope'] and not new['teacher_approved'],'Unexpected marking/scope change')
    with atomic(db):
        row=db.execute('SELECT payload,marks,review_status FROM calibrated_pathway_questions WHERE id=?',(old['id'],)).fetchone()
        require(row is not None and json.loads(row[0])==old['payload'] and row[1]==old['marks'],'Stored predecessor mismatch')
        require(row[2]=='exact_facts_checked_editorial_teacher_pending','Unexpected predecessor status')
        # Existing retirement record for the predecessor is required for this succession.
        prior=db.execute('SELECT old_payload,old_sha256 FROM difficulty_revision_history WHERE question_id=? AND revision=?',(old['id'],old['revision'])).fetchone()
        require(prior is not None and digest(prior[0])==prior[1],'Missing or invalid earlier history')
        db.execute('INSERT INTO difficulty_revision_history VALUES (?,?,?,?,?,?)',(old['id'],row[0],row[1],row[2],digest(row[0]),new['revision']))
        updated=db.execute('UPDATE calibrated_pathway_questions SET payload=? WHERE id=? AND payload=?',(json.dumps(new['payload'],sort_keys=True,ensure_ascii=False),old['id'],row[0]))
        require(updated.rowcount==1,'Active payload update mismatch')
    return new
