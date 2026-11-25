"""Foundation WSGI application. Only explicit frontend assets are served."""
import argparse
import base64
import binascii
import getpass
import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from .db import DETAIL, HERE, UNITS, connection, search
from .evidence import counts as examiner_counts, search as examiner_search
from .practice import ModelUnavailable, generate, model_available
from .review import Conflict, bounded_text, save
from .studio import catalog as studio_catalog, generate as studio_generate
from . import studio_ai, studio_prompt, workspace

API = '/api/foundation'
ASSETS = {'/':(HERE.parent/'index.html','text/html'),'/index.html':(HERE.parent/'index.html','text/html'),
          '/foundation/web/index.html':(HERE/'web/index.html','text/html'),
          '/foundation/web/app.js':(HERE/'web/app.js','text/javascript'),
          '/foundation/web/diagrams.js':(HERE/'web/diagrams.js','text/javascript'),
          '/foundation/web/style.css':(HERE/'web/style.css','text/css'),
          '/foundation/web/worksheet.js':(HERE/'web/worksheet.js','text/javascript'),
          '/foundation/web/worksheet.css':(HERE/'web/worksheet.css','text/css')}


def credentials(username,password,salt=None):
    salt = salt or os.urandom(16)
    key = hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1)
    return {'name':username,'salt':salt.hex(),'digest':key.hex()}


def authenticate(header,users):
    if not header.startswith('Basic ') or len(header)>2000:
        return None
    try:
        user,pw = base64.b64decode(header[6:],validate=True).decode().split(':',1)
    except (ValueError,UnicodeError,binascii.Error):
        return None
    for record in users:
        if user==record['name']:
            check = credentials(user,pw,bytes.fromhex(record['salt']))
            if hmac.compare_digest(check['digest'],record['digest']):
                return user
    return None


def options(query):
    return {k:v[0] for k,v in parse_qs(query,max_num_fields=12).items()}


def get_api(dbpath,route,args,actor=None):
    unit = args.get('unit','M1')
    if unit not in UNITS:
        raise ValueError('Foundation unit required')
    if route=='studio-catalog':
        return studio_catalog(dbpath,unit)
    if route=='search':
        return search(dbpath,unit,args.get('q',''),int(args.get('limit','5')),args.get('skill',''))
    with connection(dbpath) as db:
        if route=='examiner':
            return examiner_search(db,unit,args.get('q',''),int(args.get('limit','8')),args.get('skill',''))
        if route=='workspace':
            return workspace.queue(db,actor)
        if route=='drafts':
            return [dict(id=r['id'],state=r['state'],**json.loads(r['data'])) for r in db.execute(
                'SELECT id,state,data FROM practice_drafts WHERE owner=? AND id<? ORDER BY id DESC LIMIT 11',
                (actor,int(args.get('before',2**63-1))))]
        if route=='summary':
            units=json.loads(db.execute('SELECT summary FROM state').fetchone()[0])
            for u in units:
                u.update(examiner_counts(db,u['unit']))
            return dict(units=units,
                        model=model_available(),studio_ai_configured=studio_ai.available(),skills=[dict(s) for s in db.execute('SELECT * FROM skills ORDER BY page,id')])
        if route=='papers':
            return [dict(r) for r in db.execute("""SELECT year,series,component,status,reason,paper,scheme FROM pairs
                WHERE unit=? AND (year,series,component)>(?,?,?) ORDER BY year,series,component LIMIT 51""",
                (unit,int(args.get('year','0')),args.get('series',''),args.get('component','')))]
        if route=='records':
            return [dict(r) for r in db.execute(DETAIL+""" WHERE q.paper=? AND q.id>? AND d.unit=?
               ORDER BY q.id LIMIT 21""",(args.get('paper',''),int(args.get('after','0')),unit))]
        if route=='record':
            row = db.execute(DETAIL+' WHERE q.id=?',(int(args['id']),)).fetchone()
            if row:
                version = db.execute('SELECT coalesce(max(id),0) FROM reviews WHERE question_id=?',(row['id'],)).fetchone()[0]
                evidence=examiner_search(db,row['unit'],paper=row['paper'],num=row['num'])
                return dict(row,version=version,examiner_evidence=evidence)
            raise ValueError('Unknown record')
    raise LookupError()


def dispatch(dbpath,route,data,actor):
    if route=='review':
        with connection(dbpath) as db:
            return save(db,int(data['id']),data,actor)
    if route in ('studio-prompt','studio','practice') and 'temporary' in data and type(data['temporary']) is not bool:
        raise ValueError('Temporary mode must be a boolean')
    if route=='studio-prompt':
        rows = studio_prompt.author(dbpath,data['unit'],data['prompt'])
        if data.get('temporary') is True:
            return [dict(row,state='draft') for row in rows]
        with connection(dbpath) as db, db:
            return [dict(row,id=db.execute('INSERT INTO practice_drafts(owner,data) VALUES(?,?)',
                        (actor,json.dumps(row))).lastrowid,state='draft') for row in rows]
    if route=='studio':
        mode = data.get('mode','local')
        if mode not in ('local','model'):
            raise ValueError('Choose local or model-assisted generation')
        generator = studio_ai.generate if mode=='model' else studio_generate
        rows = generator(dbpath,data['unit'],data['family'],data.get('difficulty','standard'),data.get('count',1))
        if data.get('temporary') is True:
            return [dict(row,state='draft') for row in rows]
        with connection(dbpath) as db, db:
            return [dict(row,id=db.execute('INSERT INTO practice_drafts(owner,data) VALUES(?,?)',
                        (actor,json.dumps(row))).lastrowid,state='draft') for row in rows]
    if route=='practice':
        practice = generate(dbpath,data['skill'],data.get('mode','local'))
        if data.get('temporary') is True:
            return dict(practice,state='draft')
        with connection(dbpath) as db, db:
            draft_id = db.execute('INSERT INTO practice_drafts(owner,data) VALUES(?,?)',
                                  (actor,json.dumps(practice))).lastrowid
        return dict(practice,id=draft_id,state='draft')
    if route=='decision':
        with connection(dbpath) as db:
            return workspace.decide(db,actor,data)
    if route=='approve':
        with connection(dbpath) as db:
            return workspace.approve(db,actor,data)
    raise LookupError()


def application(env,start):
    path = env.get('PATH_INFO','')
    method = env.get('REQUEST_METHOD','GET')
    def send(status,body,mime='application/json',extra=()):
        data = body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode()
        headers = [('Content-Type',mime+'; charset=utf-8'),('Content-Length',str(len(data))),
                   ('Cache-Control','private, no-store'),('X-Content-Type-Options','nosniff'),
                   ('Referrer-Policy','no-referrer'),*extra]
        start(status,headers)
        return [data]
    if path not in ASSETS and not path.startswith(API+'/'):
        return send('404 Not Found',{'error':'Page not found'})
    try:
        actor = None
        if path not in ('/','/index.html'):
            config = os.environ.get('KB_USERS')
            if not config:
                return send('503 Service Unavailable',{'error':'Teacher access has not been configured'})
            actor = authenticate(env.get('HTTP_AUTHORIZATION',''),json.loads(Path(config).read_text()))
            if not actor:
                return send('401 Unauthorized',{'error':'Teacher credentials required'},extra=[
                    ('WWW-Authenticate','Basic realm="Foundation curriculum", charset="UTF-8"')])
        if path in ASSETS and method=='GET':
            target,mime = ASSETS[path]
            return send('200 OK',target.read_bytes(),mime)
        dbpath = os.environ.get('KB_DB','')
        if not Path(dbpath).is_file():
            return send('503 Service Unavailable',{'error':'The Foundation database is unavailable'})
        route = path.removeprefix(API+'/')
        if method=='GET':
            value = get_api(dbpath,route,options(env.get('QUERY_STRING','')),actor)
        elif method=='POST':
            if env.get('CONTENT_TYPE','').split(';')[0]!='application/json' or env.get('HTTP_X_KB_REQUEST')!='teacher':
                return send('415 Unsupported Media Type',{'error':'Use the teacher application'})
            length = int(env.get('CONTENT_LENGTH') or 0)
            if not 0<length<=16384:
                return send('413 Content Too Large',{'error':'Invalid request size'})
            body = json.loads(env['wsgi.input'].read(length))
            if not isinstance(body,dict):
                raise ValueError('Expected a JSON object')
            value = dispatch(dbpath,route,body,actor)
        else:
            return send('405 Method Not Allowed',{'error':'Unsupported method'})
        return send('200 OK',value)
    except (ValueError,KeyError,TypeError) as exc:
        return send('400 Bad Request',{'error':str(exc)[:200]})
    except Conflict as exc:
        return send('409 Conflict',{'error':str(exc)})
    except studio_ai.StudioAIUnavailable as exc:
        return send('503 Service Unavailable',{'error':str(exc)})
    except (ModelUnavailable,FileNotFoundError,sqlite3.OperationalError):
        return send('503 Service Unavailable',{'error':'The database or configured service is unavailable'})
    except LookupError:
        return send('404 Not Found',{'error':'Unknown endpoint'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-user',metavar='NAME')
    parser.add_argument('--port',type=int,default=8080)
    args = parser.parse_args()
    if args.add_user:
        path = Path(os.environ['KB_USERS'])
        # Exclusive create: avoid clobbering existing teacher credentials.
        password = getpass.getpass('Password: ')
        if not password or ':' in args.add_user:
            parser.error('A valid name and non-empty password are required')
        with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
            json.dump([credentials(args.add_user,password)],f)
        return
    with make_server('127.0.0.1',args.port,application) as srv:
        srv.serve_forever()


if __name__=='__main__':
    main()
