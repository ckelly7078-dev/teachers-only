"""Optional isolated Chromium smoke test: python tests/browser_diagrams.py.

Requires Playwright Python and Chromium; CHROMIUM_PATH can override the executable.
This does not exercise the full authenticated server or teacher dashboard.
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from foundation.contextual import diagram

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844})
    page.set_content('<style>body{font-family:Arial;margin:12px}.studio-diagram{margin:12px 0;max-width:480px}.studio-diagram svg{display:block;width:100%;height:auto}</style><main></main>')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_script_tag(path=str(ROOT/'foundation/web/diagrams.js'))
    for family in ('l-shape','trapezium','pythagoras'):
        for values in ((2,2,2),(18,18,18)):
            d=diagram(family,*values)
            result=page.evaluate('''d=>{let fig=renderStudioDiagram(d);document.querySelector('main').append(fig);let svg=fig.querySelector('svg');return {texts:[...svg.querySelectorAll('text')].map(x=>x.textContent),bounds:[...svg.querySelectorAll('text')].map(x=>{let b=x.getBBox();return b.x>=0 && b.y>=0 && b.x+b.width<=480 && b.y+b.height<=280}),width:svg.getBoundingClientRect().width,role:svg.getAttribute('role'),caption:fig.querySelector('figcaption').textContent}}''',d)
            assert result['texts']==[l[2] for l in d['labels']] and all(result['bounds']) and result['width']<=390 and result['role']=='img' and 'not drawn to scale' in result['caption']
    d=diagram('l-shape',3,5,7)
    d['labels'][0][2]='<script>alert(1)</script>'
    assert page.evaluate('''d=>{let f=renderStudioDiagram(d);return !f.querySelector('script')&&f.querySelector('text').textContent===d.labels[0][2]}''',d)
    d['polygon'][0][0]='0 onload=alert(1)'
    assert page.evaluate('d=>renderStudioDiagram(d)===null',d)
    assert not errors,errors
    browser.close()
print('Six mobile schematic render checks and two malformed/injection input checks passed.')
