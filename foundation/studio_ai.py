"""Optional OpenAI selection of locally validated original questions. No raw source text."""
import json
import os
import re
import urllib.request
from . import studio

ENDPOINT = 'https://api.openai.com/v1/responses'
MAX_RESPONSE = 65536


class StudioAIUnavailable(Exception):
    pass


def available():
    return bool(os.environ.get('OPENAI_API_KEY','').strip() and
                re.fullmatch(r'[A-Za-z0-9._:-]{1,100}',os.environ.get('KB_STUDIO_MODEL','')))


# Only these pre-reviewed lexical substitutions are permitted, never model prose.
VARIANTS = {
    'percent': ('Find ', 'Calculate '),
    'fraction': ('Find ', 'Calculate '),
    'equation': ('Solve ', 'Find x by solving '),
    'rounding': ('Round ', 'Give '),  # handled separately below
    'area': ('Find its area', 'Calculate its area'),
    'hcf': ('Find the ', 'Calculate the '),
    'lcm': ('Find the ', 'Calculate the '),
    'midpoint': ('Find the ', 'Calculate the '),
    'ratio': (' counters ', ' tokens '),
    'sequence': ('Write the next two terms', 'State the next two terms'),
    'binary': ('Convert the binary number ', 'Express the binary number '),
    'nth-term': ('Find an expression', 'Write an expression'),
    'indices': ('Write ', 'Express '),
    'shopping-discount': ('A sports shop', 'A cycling shop'),
    'discount-budget': ('A club', 'A community group'),
    'l-shape': ('An L-shaped floor', 'An L-shaped workshop floor'),
    'trapezium': ('A trapezium-shaped garden', 'A trapezium-shaped lawn'),
    'pythagoras': ('A rectangular frame', 'A rectangular metal frame'),
    'map-scale': ('A route consists of', 'A walking route consists of'),
    'expected-frequency': ('A bag contains', 'An opaque container holds'),
    'gradient': ('A straight line passes through', 'A straight line contains the points'),
}


def variants(row):
    q=row['question']; family=row['family']
    if family=='rounding':
        alt=q.replace('Round ','Give ',1).replace(' to the nearest ',' rounded to the nearest ',1)
    elif family=='binary':
        alt=q.replace('Convert the binary number ','Express the binary number ',1).replace(' to decimal ',' in decimal ',1)
    else:
        old,new=VARIANTS[family]; alt=q.replace(old,new,1)
    # Labels must not change digits, arithmetic, units, diagram instructions or subpart count.
    if alt==q or re.findall(r'\d+',q)!=re.findall(r'\d+',alt):
        raise ValueError('Invalid curated wording variant')
    return [q,alt]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def send(payload):
    if not available():
        raise StudioAIUnavailable('AI Studio is not configured')
    data=json.dumps(payload,ensure_ascii=True).encode()
    if len(data)>32768: raise StudioAIUnavailable('AI request exceeds its size limit')
    req=urllib.request.Request(ENDPOINT,data=data,headers={
        'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'], 'Content-Type':'application/json'},method='POST')
    try:
        # No redirects or inherited proxy settings; never forward the project key elsewhere.
        opener=urllib.request.build_opener(NoRedirect(),urllib.request.ProxyHandler({}))
        with opener.open(req,timeout=20) as resp:
            raw=resp.read(MAX_RESPONSE+1)
        if len(raw)>MAX_RESPONSE: raise ValueError('Oversize response')
        return json.loads(raw)
    except (OSError,ValueError,TypeError) as exc:
        raise StudioAIUnavailable('AI service unavailable; use local generation or retry later') from exc


def unique_keys(pairs):
    result={}
    for k,v in pairs:
        if k in result: raise ValueError('Duplicate response field')
        result[k]=v
    return result


def selection(response,pool,count):
    try:
        if response['status']!='completed': raise ValueError('Incomplete response')
        content=[part for item in response['output'] if item['type']=='message'
                 for part in item['content']]
        if len(content)!=1 or content[0]['type']!='output_text': raise ValueError('Refused or malformed response')
        obj=json.loads(content[0]['text'],object_pairs_hook=unique_keys)
        if type(obj) is not dict or set(obj)!={'selection'}: raise ValueError('Unexpected fields')
        rows=obj['selection']
        if type(rows) is not list or len(rows)!=count: raise ValueError('Wrong selection count')
        seen=set(); result=[]
        for item in rows:
            if type(item) is not dict or set(item)!={'id','variant'}: raise ValueError('Unexpected selection fields')
            i,v=item['id'],item['variant']
            if type(i) is not int or type(v) is not int or not 0<=i<len(pool) or v not in (0,1) or i in seen:
                raise ValueError('Invalid or repeated selection')
            seen.add(i); row=pool[i]; q=variants(row)[v]
            result.append(dict(row,question=q,mode='model',model_role='Selected validated candidate and curated wording',
                               validation='Independent numeric check passed before AI selection; proposed rubric requires teacher review'))
        return result
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise StudioAIUnavailable('AI returned an invalid selection; no drafts saved') from exc


def generate(path,unit,family,difficulty='standard',count=1):
    if not available(): raise StudioAIUnavailable('AI Studio is not configured')
    if type(count) is not int or not 1<=count<=10: raise ValueError('Choose 1 to 10 questions')
    pool=[]; seen=set()
    batch=min(10,max(4,count))
    for _ in range(2):
        for row in studio.generate(path,unit,family,difficulty,batch):
            if row['question'] not in seen:
                seen.add(row['question']); pool.append(row)
    first=pool[0]
    context=dict(unit=unit,family=family,difficulty=difficulty,count=count,
                 skill=first['skill_label'],spec_page=first['spec_page'],
                 reference_marks=[r['marks'] for r in first['sources']],
                 evidence_level=first['evidence_level'],
                 candidates=[dict(id=i,wording=variants(row),marks=row['marks']) for i,row in enumerate(pool)])
    schema={'type':'object','additionalProperties':False,'required':['selection'],'properties':{
        'selection':{'type':'array','items':{'type':'object','additionalProperties':False,
            'required':['id','variant'],'properties':{'id':{'type':'integer','enum':list(range(len(pool)))},
                                                       'variant':{'type':'integer','enum':[0,1]}}}}}}
    payload=dict(model=os.environ['KB_STUDIO_MODEL'],store=False,max_output_tokens=600,
                 instructions='Select exactly the requested number of distinct candidate IDs and one wording index (0 or 1) for each. Prefer varied, readable Foundation practice within the given family. Return only the selection. Do not generate new text, alter values, or infer official CCEA approval.',
                 input=json.dumps(context,ensure_ascii=True),text={'format':{'type':'json_schema','name':'studio_selection','strict':True,'schema':schema}})
    return selection(send(payload),pool,count)
