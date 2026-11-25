"""Teacher-owned review queue and non-destructive draft decisions.

Uses the existing practice_drafts table; no source-knowledge records or schema
migration are required. State is persisted independently of browser sessions.
"""
import json
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


def queue(db, actor):
    # Ascending creation order gives stable worksheet numbering across batches.
    return [public_row(r) for r in db.execute(
        'SELECT id,state,data FROM practice_drafts WHERE owner=? ORDER BY id', (actor,))]


def decide(db, actor, data):
    qid, expected, target = data['id'], data['expected'], data['state']
    if type(qid) is not int or qid < 1 or expected not in STATES or target not in TRANSITIONS[expected]:
        raise ValueError('Invalid question decision')
    db.execute('BEGIN IMMEDIATE')
    with db:
        row = db.execute('SELECT id,state,data FROM practice_drafts WHERE id=? AND owner=?', (qid, actor)).fetchone()
        if not row or row['state'] != expected:
            raise Conflict('Question changed or is unavailable. Reload the workspace.')
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
