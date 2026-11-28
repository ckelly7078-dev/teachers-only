"""Authenticated localhost AS1 preview and evidence collection; no release endpoint.

Mount only a private, hash-verified BQ snapshot. No arbitrary paths, live TeX,
source PDFs, external scripts, pupil identities or credentials in the response.
"""
import argparse
import base64
import binascii
import copy
import datetime
import getpass
import hashlib
import hmac
import json
import os
import sqlite3
from contextlib import closing
import sys
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
from active_difficulty import MODES, require
from marking_review import fingerprint
from marking_batch import read_batch
from readiness_bo import conservative_preview_eligible
from successor_bq import SuccessorResolver, REVISION

ASSETS = {'/': ('review_bq.html', 'text/html'), '/app.js': ('review_bq.js', 'text/javascript'), '/style.css': ('review_bq.css', 'text/css')}
PRIVATE_FILES = ('as1.sqlite', 'FM16BQ-successor-edits.jsonl', 'FM16BQ-page-index.jsonl', 'FM16BQ-teacher-preview.pdf')
CHECKS = ('visual', 'mathematics', 'marking', 'scope', 'difficulty')


def sha_file(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


class PrivateCatalogue:
    def __init__(self, root):
        import fitz
        root = Path(root).resolve()
        manifest = json.loads((root/'FM16BQ-runtime-manifest.json').read_text())
        require(manifest['checkpoint'] == REVISION and set(manifest['sha256']) == set(PRIVATE_FILES), 'Invalid private manifest')
        for name in PRIVATE_FILES:
            require(sha_file(root/name) == manifest['sha256'][name], 'Private snapshot hash mismatch')
        self.resolver = SuccessorResolver(read_batch(root/PRIVATE_FILES[1]))
        self.resolver.verify(root/PRIVATE_FILES[0])
        rows = read_batch(root/PRIVATE_FILES[2]); self.pages = {r['id']: r for r in rows}
        require(len(rows) == len(self.pages) == 2106 and sorted(r['page'] for r in rows) == list(range(1,2107)), 'Invalid page index')
        self.proof = (root/PRIVATE_FILES[3]).read_bytes()
        self.proof_sha256 = hashlib.sha256(self.proof).hexdigest()
        require(self.proof_sha256 == manifest['sha256'][PRIVATE_FILES[3]], 'Proof changed during load')
        self.items = {}; self.modes = {m: [] for m in MODES}
        with fitz.open(stream=self.proof, filetype='pdf') as doc:
            require(len(doc) == len(rows), 'Proof count mismatch')
            for p in sorted(self.resolver.bases):
                for t in range(1,7):
                    for v in (1,2,3):
                        item = self.resolver._resolve(p,t,v); key = item['id']; row = self.pages[key]
                        require(row['fingerprint'] == fingerprint(item) and row['revision'] == item['revision'] and row['teacher_approved'] is False, 'Stale page record')
                        text = doc[row['page']-1].get_text()
                        require(key in text and item['revision'] in text, 'Proof page identity mismatch')
                        self.items[key] = item
                        for mode in MODES:
                            if conservative_preview_eligible(self.resolver,p,t,mode): self.modes[mode].append(key)
        self.allowed = {m: frozenset(ids) for m,ids in self.modes.items()}
        require(not self.allowed['approved_exam'], 'Unexpected approved exams')

    def list_ids(self, mode):
        require(isinstance(mode,str) and mode in self.modes, 'Unknown preview mode')
        return self.modes[mode][:]

    def get(self, key, mode):
        require(isinstance(mode,str) and mode in self.allowed and isinstance(key,str) and key in self.allowed[mode], 'Preview not eligible')
        item = copy.deepcopy(self.items[key]); row = self.pages[key]
        return {'item': item, 'mode': mode, 'fingerprint': row['fingerprint'], 'proof_sha256': self.proof_sha256, 'page': row['page'], 'release_allowed': False, 'exam_ready': False}

    def png(self, key, mode):
        import fitz
        self.get(key,mode)
        with fitz.open(stream=self.proof,filetype='pdf') as doc:
            return doc[self.pages[key]['page']-1].get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).tobytes('png')


def credentials(name,password,salt=None):
    require(isinstance(name,str) and name and ':' not in name and isinstance(password,str) and password, 'Invalid credentials')
    salt = salt or os.urandom(16)
    return {'name':name,'salt':salt.hex(),'digest':hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1).hex()}


def authenticate(header,users):
    if not header.startswith('Basic ') or len(header)>2000: return None
    try:
        name,pw = base64.b64decode(header[6:],validate=True).decode().split(':',1)
        for u in users:
            if name == u['name'] and hmac.compare_digest(credentials(name,pw,bytes.fromhex(u['salt']))['digest'],u['digest']): return name
    except (ValueError,UnicodeError,binascii.Error,KeyError,TypeError): pass
    return None


def save_review(path, actor, item, data):
    require(set(data) == {'id','mode','fingerprint','proof_sha256','checks','note'}, 'Unexpected review fields')
    require(data['id'] == item['item']['id'] and data['fingerprint'] == item['fingerprint'] and data['proof_sha256'] == item['proof_sha256'], 'Stale review')
    checks = data['checks']; note = data['note']
    require(isinstance(checks,dict) and set(checks) == set(CHECKS) and all(v in ('pass','revise','not_reviewed') for v in checks.values()), 'Invalid review decisions')
    require(isinstance(note,str) and 1 <= len(note.strip()) <= 2000, 'Review evidence note required')
    # Deliberately record observations only; no teacher-approved flag or tier change.
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS observations (seq INTEGER PRIMARY KEY, actor TEXT NOT NULL, item_id TEXT NOT NULL, fingerprint TEXT NOT NULL, revision TEXT NOT NULL, proof_sha256 TEXT NOT NULL, observed_utc TEXT NOT NULL, checks TEXT NOT NULL, note TEXT NOT NULL)')
        seq=db.execute('INSERT INTO observations(actor,item_id,fingerprint,revision,proof_sha256,observed_utc,checks,note) VALUES (?,?,?,?,?,?,?,?)',(actor,data['id'],data['fingerprint'],item['item']['revision'],item['proof_sha256'],datetime.datetime.now(datetime.timezone.utc).isoformat(),json.dumps(checks,sort_keys=True),note.strip())).lastrowid
    return {'observation_id':seq,'release_allowed':False,'teacher_approved':False}


def check_ledger_path(ledger, protected):
    if ledger is None:
        return
    ledger = Path(ledger).resolve()
    for candidate in protected:
        target = Path(candidate).resolve()
        require(ledger != target and not (ledger.exists() and target.exists() and ledger.samefile(target)),
                'Review ledger must be separate from the catalogue, Foundation database and credentials')


def application(catalogue,users,review_db=None):
    def app(env,start):
        def send(status,body,mime='application/json',extra=()):
            raw=body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode()
            start(status,[('Content-Type',mime+('; charset=utf-8' if mime!='image/png' else '')),('Content-Length',str(len(raw))),('Cache-Control','private, no-store'),('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer'),('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"),*extra]);return [raw]
        actor=authenticate(env.get('HTTP_AUTHORIZATION',''),users)
        if actor is None: return send('401 Unauthorized',{'error':'Teacher credentials required'},extra=[('WWW-Authenticate','Basic realm="AS1 teacher preview", charset="UTF-8"')])
        method=env.get('REQUEST_METHOD'); path=env.get('PATH_INFO','')
        try:
            if method=='GET' and path in ASSETS:
                name,mime=ASSETS[path]
                body=(Path(__file__).parent/name).read_bytes()
                if path == '/' and env.get('teachers_only.as1_mounted'):
                    body = body.replace(b'<!--MOUNT_NAV-->', b'<nav aria-label="Related workspaces"><a href="/index.html">Teacher portal</a> &middot; <a href="/foundation/web/index.html">Foundation Mathematics Studio</a></nav>')
                return send('200 OK',body,mime)
            if method=='GET' and path in ('/api/list','/api/item','/api/page'):
                qs=parse_qs(env.get('QUERY_STRING',''),keep_blank_values=True,max_num_fields=2,strict_parsing=True)
                require(all(len(v)==1 for v in qs.values()), 'Duplicate query parameter')
                mode=qs['mode'][0]
                if path=='/api/list':
                    require(set(qs)=={'mode'},'Invalid query parameters');return send('200 OK',{'ids':catalogue.list_ids(mode),'release_allowed':False})
                require(set(qs)=={'mode','id'},'Invalid query parameters');key=qs['id'][0]
                if path=='/api/item': return send('200 OK',catalogue.get(key,mode))
                return send('200 OK',catalogue.png(key,mode),'image/png')
            if method=='POST' and path=='/api/review':
                if review_db is None:return send('503 Service Unavailable',{'error':'Review recording not configured'})
                if env.get('CONTENT_TYPE','').split(';')[0]!='application/json' or env.get('HTTP_X_AS1_REQUEST')!='teacher':return send('415 Unsupported Media Type',{'error':'Use the teacher review application'})
                length=int(env.get('CONTENT_LENGTH') or 0);require(0<length<=16384,'Invalid request size')
                data=json.loads(env['wsgi.input'].read(length));require(isinstance(data,dict),'Review object required')
                return send('200 OK',save_review(review_db,actor,catalogue.get(data['id'],data['mode']),data))
            return send('404 Not Found',{'error':'Unknown endpoint'})
        except (ValueError,KeyError,TypeError):return send('400 Bad Request',{'error':'Invalid or ineligible request'})
        except (OSError,sqlite3.Error):return send('503 Service Unavailable',{'error':'Private service unavailable'})
    return app


def mount_as1(foundation_app, as1_app):
    """Optional same-origin mount; existing Foundation and portal paths are untouched."""
    def mounted(env,start):
        path=env.get('PATH_INFO','')
        env = {**env, 'teachers_only.as1_mounted': True}
        if path=='/as1':
            start('302 Found',[('Location','/as1/'),('Cache-Control','no-store'),('Content-Length','0')]);return [b'']
        if path.startswith('/as1/'):
            local=dict(env,PATH_INFO=path[4:],SCRIPT_NAME=env.get('SCRIPT_NAME','')+'/as1')
            return as1_app(local,start)
        return foundation_app(env,start)
    return mounted


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle',type=Path);parser.add_argument('--users',type=Path,required=True);parser.add_argument('--review-db',type=Path);parser.add_argument('--port',type=int,default=8081);parser.add_argument('--add-user');parser.add_argument('--with-foundation',action='store_true')
    args=parser.parse_args()
    if args.add_user:
        user=credentials(args.add_user,getpass.getpass('Password: '))
        with os.fdopen(os.open(args.users,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump([user],f)
        return
    require(args.bundle is not None,'Private bundle required')
    protected = [args.users, *(args.bundle / name for name in PRIVATE_FILES)]
    if args.with_foundation:
        protected.extend(os.environ[name] for name in ('KB_DB', 'KB_USERS') if os.environ.get(name))
    check_ledger_path(args.review_db, protected)
    users=json.loads(args.users.read_text());require(isinstance(users,list) and users,'Teacher credentials required')
    app=application(PrivateCatalogue(args.bundle),users,args.review_db)
    if args.with_foundation:
        sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
        from foundation.server import application as foundation_app
        app=mount_as1(foundation_app,app)
    with make_server('127.0.0.1',args.port,app) as server:server.serve_forever()


if __name__=='__main__':main()
