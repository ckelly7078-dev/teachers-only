"""Teacher-owned review queue and non-destructive draft decisions.

Uses the existing practice_drafts table; no source-knowledge records or schema
migration are required. State is persisted independently of browser sessions.
"""
import json
import re
from .review import Conflict, bounded_text

STATES = ('draft', 'under_review', 'approved', 'discarded')
TRANSITIONS = {
    'draft': {'under_review', 'discarded'},
    'under_review': {'discarded', 'draft'},
    'approved': {'under_review', 'discarded'},
    'discarded': {'draft'},
}


def public_row(row):
    return dict(json.loads(row['data']), id=row['id'], state=row['state'])


WORKSHEET = re.compile(r'(?:general|class-[1-9][0-9]{0,15}):[0-9a-f]{32}')

def worksheet_key(value):
    if value == 'legacy' or (isinstance(value, str) and WORKSHEET.fullmatch(value)):
        return value
    raise ValueError('Invalid worksheet identifier')


def tag_rows(rows, data):
    if 'worksheet' not in data:
        return rows
    key = worksheet_key(data['worksheet'])
    return [dict(row, worksheet_id=key) for row in rows]


def row_worksheet(row):
    return json.loads(row['data']).get('worksheet_id') or 'legacy'


def queue(db, actor, worksheet=None):
    sql = 'SELECT id,state,data FROM practice_drafts WHERE owner=?'
    params = [actor]
    if worksheet is not None:
        sql += " AND coalesce(json_extract(data,'$.worksheet_id'),'legacy')=?"
        params.append(worksheet_key(worksheet))
    return [public_row(r) for r in db.execute(sql+' ORDER BY id', params)]


def collections(db, actor):
    rows = db.execute("""SELECT coalesce(json_extract(data,'$.worksheet_id'),'legacy') AS worksheet,
        count(*) AS questions, sum(state='approved') AS approved, max(created) AS latest
        FROM practice_drafts WHERE owner=? GROUP BY worksheet ORDER BY latest DESC, worksheet""", (actor,))
    return [dict(row) for row in rows]


def check_worksheet(row, data):
    if 'worksheet' in data and row_worksheet(row) != worksheet_key(data['worksheet']):
        raise Conflict('Question belongs to another worksheet. Reload before changing it.')


def decide(db, actor, data):
    qid, expected, target = data['id'], data['expected'], data['state']
    if type(qid) is not int or qid < 1 or expected not in STATES or target not in TRANSITIONS[expected]:
        raise ValueError('Invalid question decision')
    db.execute('BEGIN IMMEDIATE')
    with db:
        row = db.execute('SELECT id,state,data FROM practice_drafts WHERE id=? AND owner=?', (qid, actor)).fetchone()
        if not row or row['state'] != expected:
            raise Conflict('Question changed or is unavailable. Reload the workspace.')
        check_worksheet(row, data)
        db.execute('UPDATE practice_drafts SET state=?, approved=NULL WHERE id=? AND owner=?', (target, qid, actor))
        return dict(public_row(row), state=target)


def approve(db, actor, data):
    qid = data['id']
    if type(qid) is not int or qid < 1:
        raise ValueError('Invalid question identifier')
    db.execute('BEGIN IMMEDIATE')
    with db:
        row = db.execute('SELECT id,state,data FROM practice_drafts WHERE id=? AND owner=?', (qid, actor)).fetchone()
        # Preserve the legacy direct-draft approval API; the new UI requires review.
        if not row or row['state'] not in ('draft', 'under_review'):
            raise Conflict('This draft is unavailable or already decided')
        if 'expected' in data and data['expected'] != row['state']:
            raise Conflict('Question changed. Reload the workspace.')
        check_worksheet(row, data)
        practice = json.loads(row['data'])
        question = bounded_text(data['question'], 1500, 'question')
        if question != practice['question'] and practice.get('family'):
            raise Conflict('Studio question edits require a new validated draft; regenerate instead')
        if question != practice['question']:
            practice['generated_question'] = practice.get('generated_question', practice['question'])
            practice['validation'] = 'Teacher edited the question and confirmed the worked solution and marks'
        practice['question'] = question
        db.execute("UPDATE practice_drafts SET data=?,state='approved',approved=CURRENT_TIMESTAMP WHERE id=? AND owner=?",
                   (json.dumps(practice), qid, actor))
        return dict(practice, id=qid, state='approved')
