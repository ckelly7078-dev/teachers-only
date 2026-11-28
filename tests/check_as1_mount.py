"""Exercise the combined development service with a private BQ bundle.

Run from the repository root. Foundation data, credentials and review writes
exist only for this test. --browser adds actual Chromium navigation.
"""
import argparse
import base64
from contextlib import closing
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
import threading
from unittest.mock import patch
from urllib.parse import urlencode
from wsgiref.simple_server import make_server, WSGIRequestHandler

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'further_maths')]
from foundation.db import connect, refresh
from foundation.server import application as foundation
from review_progress_br import observation_rows
from review_service_bq import CHECKS, PrivateCatalogue, application, credentials, mount_as1


class Quiet(WSGIRequestHandler):
    def log_message(self, *args):
        pass


def request(port, path, auth=None, payload=None):
    headers = {}
    if auth:
        headers['Authorization'] = 'Basic ' + base64.b64encode(':'.join(auth).encode()).decode()
    body = None
    if payload is not None:
        body = json.dumps(payload)
        headers.update({'Content-Type': 'application/json', 'X-AS1-Request': 'teacher'})
    with closing(HTTPConnection('127.0.0.1', port, timeout=30)) as client:
        client.request('GET' if body is None else 'POST', path, body, headers)
        response = client.getresponse()
        return response.status, response.read(), dict(response.getheaders())


def check_http(port, cat, foundation_auth, as1_auth, ledger):
    def get(path, status=200, auth=None, payload=None):
        code, body, headers = request(port, path, auth, payload)
        assert code == status, (path, code, status)
        return body, headers

    link = b'<a href="/as1/">AS1 Further Mathematics review</a>'
    assert link in get('/')[0] and link in get('/index.html')[0]
    assert get('/as1', 302)[1]['Location'] == '/as1/'
    for path, own, other in [('/foundation/web/index.html', foundation_auth, as1_auth),
                             ('/as1/', as1_auth, foundation_auth)]:
        get(path, 401)
        get(path, 401, other)
        html = get(path, auth=own)[0]
        assert (link if own == foundation_auth else b'href="/foundation/web/index.html"') in html
    summary = json.loads(get('/api/foundation/summary', auth=foundation_auth)[0])
    assert [row['unit'] for row in summary['units']] == ['M1', 'M2', 'M5', 'M6']
    assert json.loads(get('/api/foundation/search?q=fictional', auth=foundation_auth)[0]) == []
    get('/api/foundation/summary', 401, as1_auth)
    get('/as1/api/list?mode=learning_preview', 401, foundation_auth)
    results = {}
    for mode, expected in cat.modes.items():
        listing = json.loads(get('/as1/api/list?mode=' + mode, auth=as1_auth)[0])
        assert listing == {'ids': expected, 'release_allowed': False}
        results[mode] = len(expected)
        if not expected:
            continue
        key = expected[len(expected) // 2]
        query = urlencode({'mode': mode, 'id': key})
        item = json.loads(get('/as1/api/item?' + query, auth=as1_auth)[0])
        assert item['fingerprint'] == cat.pages[key]['fingerprint'] and item['exam_ready'] is False
        assert item['proof_sha256'] == cat.proof_sha256 and item['release_allowed'] is False
        png, headers = get('/as1/api/page?' + query, auth=as1_auth)
        assert headers['Content-Type'] == 'image/png' and png == cat.png(key, mode)
        data = dict(id=key, mode=mode, fingerprint=item['fingerprint'], proof_sha256=cat.proof_sha256,
                    checks={k: 'not_reviewed' for k in CHECKS}, note='Disposable transport fixture.')
        get('/as1/api/review', 400, as1_auth, {**data, 'fingerprint': '0' * 64})
        saved = json.loads(get('/as1/api/review', auth=as1_auth, payload=data)[0])
        assert saved['teacher_approved'] is False and saved['release_allowed'] is False
        row = observation_rows(ledger)[-1]
        assert (row['item_id'], row['actor'], row['fingerprint'], row['proof_sha256']) == (
            key, as1_auth[0], item['fingerprint'], cat.proof_sha256)
    key = cat.list_ids('learning_preview')[0]
    for route in ('item', 'page'):
        get('/as1/api/' + route + '?' + urlencode({'mode': 'approved_exam', 'id': key}), 400, as1_auth)
    assert len(observation_rows(ledger)) == 4
    return results


def check_browser(port, auth, executable):
    from playwright.sync_api import sync_playwright
    origin = f'http://127.0.0.1:{port}'
    with sync_playwright() as pw, pw.chromium.launch(executable_path=executable) as browser:
        for width, height in ((1280, 900), (390, 844), (320, 720)):
            with browser.new_context(viewport={'width': width, 'height': height},
                                     http_credentials={'username': auth[0], 'password': auth[1], 'origin': origin}) as context:
                page = context.new_page()
                page.goto(origin)
                page.get_by_role('button', name='Teacher', exact=False).first.click()
                page.get_by_role('button', name='Continue as Mr Stephenson').click()
                tiles = page.locator('button.staff-tile')
                assert tiles.count() == 9
                for index in range(9):
                    tiles.nth(index).click()
                    page.get_by_role('button', name='Back to workspace').first.click()
                    assert tiles.count() == 9
                page.get_by_role('link', name='AS1 Further Mathematics review').click()
                for mode in ('learning_preview', 'exam_candidate_preview', 'challenge_preview', 'enrichment_preview'):
                    page.select_option('#mode', mode)
                    page.wait_for_function("document.querySelector('#item').options.length > 1")
                    page.locator('#browse button').click()
                    page.wait_for_function("!document.querySelector('#proof-zoom').disabled && document.querySelector('#proof').naturalWidth > 0")
                    page.locator('#proof-zoom').focus()
                    page.keyboard.press('Space')
                    assert page.locator('#proof-zoom').get_attribute('aria-pressed') == 'true'
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    page.fill('#note', 'Disposable browser fixture.')
                    page.locator('#review button').click()
                    page.wait_for_function("document.querySelector('#review-status').textContent.includes('saved')")
                    page.select_option('#item', index=1)
                    assert page.locator('#preview').is_hidden() and page.locator('#review button').is_disabled()
                page.get_by_role('link', name='Foundation Mathematics Studio').click()
                page.get_by_role('heading', name='Mathematics Studio', exact=True).wait_for()
                page.get_by_role('link', name='AS1 Further Mathematics review').click()
                page.locator('#browse').wait_for()
    return 12


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--browser', action='store_true')
    parser.add_argument('--chromium', help='Optional installed Chromium executable')
    args = parser.parse_args()
    cat = PrivateCatalogue(args.bundle)
    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        foundation_db, users, ledger = (temp / n for n in ('foundation.sqlite', 'users.json', 'observations.sqlite'))
        with closing(connect(foundation_db, True)) as db, db:
            refresh(db)
        fa, aa, both = [(name, secrets.token_urlsafe(24)) for name in ('fixture-foundation', 'fixture-as1', 'fixture-both')]
        shared = credentials(*both)
        users.write_text(json.dumps([credentials(*fa), shared]))
        app = mount_as1(foundation, application(cat, [credentials(*aa), shared], ledger))
        with patch.dict(os.environ, {'KB_DB': str(foundation_db), 'KB_USERS': str(users)}), \
                make_server('127.0.0.1', 0, app, handler_class=Quiet) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                counts = check_http(server.server_port, cat, fa, aa, ledger)
                result = {'http_integration': True, 'modes': counts, 'foundation_fixture_units': 4,
                          'http_fixture_writes': 4, 'browser_cases': 0, 'production_host_tested': False}
                if args.browser:
                    result['browser_cases'] = check_browser(server.server_port, both, args.chromium)
                    assert len(observation_rows(ledger)) == 4 + result['browser_cases']
            finally:
                server.shutdown()
                thread.join()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
