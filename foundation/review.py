"""Review a single source-linked record and atomically update the search index."""
import json
import re

from .db import DETAIL, index_question, refresh


class Conflict(Exception):
    pass


def bounded_text(value, maximum, name):
    if not isinstance(value,str) or not value.strip() or len(value)>maximum:
        raise ValueError(f'Invalid {name}')
    return value.strip()


def save(db, qid, data, actor):
    db.execute('BEGIN IMMEDIATE')
    with db:
        old = db.execute(DETAIL+' WHERE q.id=?',(qid,)).fetchone()
        if not old:
            raise ValueError('Unknown question')
        last = db.execute('SELECT coalesce(max(id),0) FROM reviews WHERE question_id=?',(qid,)).fetchone()[0]
        if data.get('version')!=last:
            raise Conflict('The record changed. Reload before saving.')
        valid_pair = db.execute("SELECT 1 FROM pairs WHERE paper=? AND scheme=? AND status='paired'",
                                (old['paper'],old['scheme'])).fetchone()
        if not valid_pair:
            raise ValueError('Resolve the document pairing before verification')
        state = data.get('status')
        if state not in ('review','verified'):
            raise ValueError('Invalid review state')
        skill = db.execute('SELECT id FROM skills WHERE id=? AND unit=?',(data['skill'],old['unit'])).fetchone()
        if not skill:
            raise ValueError('Choose a skill from the unit taxonomy')
        marks = data['marks']
        if type(marks) is not int or not 1<=marks<=100:
            raise ValueError('Invalid mark total')
        for key,source in [('page','paper'),('end_page','paper'),('scheme_page','scheme')]:
            pages = db.execute('SELECT pages FROM documents WHERE sha=?',(old[source],)).fetchone()[0]
            if type(data[key]) is not int or not 1<=data[key]<=pages:
                raise ValueError('Source page outside document')
        if data['end_page']<data['page']:
            raise ValueError('Invalid paper page range')
        routes = data['rules']
        if not isinstance(routes,list) or not 1<=len(routes)<=5:
            raise ValueError('Supply one to five alternative marking routes')
        for route in routes:
            if not isinstance(route,list) or not 1<=len(route)<=20:
                raise ValueError('Invalid criterion list')
            total = 0
            for criterion in route:
                if not isinstance(criterion,dict):
                    raise ValueError('Invalid criterion format')
                code = re.fullmatch(r'(MA|M|A|B)([1-9]\d?)',str(criterion.get('code','')))
                if not code:
                    raise ValueError('Invalid marking code')
                total += int(code[2])
                bounded_text(criterion.get('evidence'),240,'criterion evidence')
                if set(criterion)!={'code','evidence'}:
                    raise ValueError('Unknown criterion field')
            if total!=marks:
                raise ValueError('Each alternative must add up to the available marks')
        annotation = bounded_text(data['annotation'],600,'instructional note')
        answer = bounded_text(data['answer'],300,'answer')
        depends = data.get('depends_on') or None
        if depends and not db.execute("""SELECT 1 FROM questions WHERE paper=? AND id!=?
                           AND (CAST(num AS TEXT)||'.'||part)=? AND num<=?""",
                           (old['paper'],qid,depends,old['num'])).fetchone():
            raise ValueError('Unknown prerequisite question')
        codes = []
        for criterion in (c for route in routes for c in route):
            if criterion['code'] not in codes:
                codes.append(criterion['code'])
        db.execute("""UPDATE questions SET codes=?,skill=?,annotation=?,answer=?,rules=?,marks=?,page=?,end_page=?,
                   scheme_page=?,status=?,verified_by=?,depends_on=?,extraction_note=NULL WHERE id=?""",
                   (json.dumps(codes),skill[0],annotation,answer,json.dumps(routes),marks,data['page'],data['end_page'],
                    data['scheme_page'],state,actor,depends,qid))
        new = dict(db.execute(DETAIL+' WHERE q.id=?',(qid,)).fetchone())
        db.execute('INSERT INTO reviews(question_id,actor,before_json,after_json) VALUES(?,?,?,?)',
                   (qid,actor,json.dumps(dict(old)),json.dumps(new)))
        index_question(db,qid)
        refresh(db)
        return new
