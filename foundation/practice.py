"""Original M1 practice from bounded references and constrained integer parameters."""
import json
import os
import secrets
import urllib.error
import urllib.request
from fractions import Fraction

from .db import SPEC, search

SKILLS = {'percentage','metric','finance'}
MODES = {'local','model'}


class ModelUnavailable(Exception):
    pass


def model_available():
    return all(os.environ.get(k) for k in ('KB_MODEL_URL','KB_MODEL_KEY','KB_MODEL_NAME'))


def parameters(refs,skill):
    if not model_available():
        raise ModelUnavailable('No model service is configured')
    # A small allowlist excludes document bodies, student work and teacher notes.
    context = [dict(skill=r['label'],source_marks=r['marks'],unit=r['unit'],spec_page=r['spec_page'])
               for r in refs[:3]]
    prompt = dict(skill=skill,reference_examples=context,instruction=
        'Select two integers a and b, each from 2 to 18, for original Foundation practice. Return JSON fields a,b only.')
    payload = json.dumps(dict(model=os.environ['KB_MODEL_NAME'],messages=[
        {'role':'user','content':json.dumps(prompt)}],max_tokens=60)).encode()
    req = urllib.request.Request(os.environ['KB_MODEL_URL'],data=payload,headers={
        'Content-Type':'application/json','Authorization':'Bearer '+os.environ['KB_MODEL_KEY']})
    try:
        with urllib.request.urlopen(req,timeout=12) as resp:
            result = json.loads(resp.read(24000))['choices'][0]['message']['content']
        obj = json.loads(result)
        a,b = obj['a'],obj['b']
        if type(a) is not int or type(b) is not int or not (2<=a<=18 and 2<=b<=18):
            raise ValueError()
        return a,b
    except (OSError,ValueError,IndexError,KeyError,TypeError) as exc:
        raise ModelUnavailable('The model returned no usable parameters') from exc


def money(pence):
    return f'£{pence//100}.{pence%100:02d}'


def validate(skill,a,b,answer):
    # Use inverse calculations on the final answer independently of the solution steps.
    if skill=='percentage':
        return Fraction(answer,100)*(20*b)==a*b
    if skill=='metric':
        return Fraction(answer+2*b,10)==Fraction(5*a+b,1)
    return answer + 3*(25*a+5*b)==2000


def generate(path,skill,mode='local'):
    if skill not in SKILLS or mode not in MODES:
        raise ValueError('Unsupported practice skill or generation mode')
    refs = search(path,'M1',skill=skill,limit=3)
    if not refs:
        raise ValueError('This skill has no verified reference examples')
    a,b = parameters(refs,skill) if mode=='model' else (2+secrets.randbelow(17),2+secrets.randbelow(17))
    if skill=='percentage':
        total,part = 20*b,a*b
        question = (f'A librarian examined {total} returned books. {total-part} could go straight back on the shelf. '
                    'What percentage needed attention? Show your calculation.')
        answer = 5*a
        display = f'{answer}%'
        steps = [f'{total} − {total-part} = {part} books.',f'{part} ÷ {total} × 100 = {answer}%.']
        rubric = ['M1 for a valid part-to-whole calculation, including a complementary percentage method.',
                  'A1 for the correct percentage from a valid method.']
    elif skill=='metric':
        length,trim = 5*a+b,2*b
        question = (f'A maker marks out a strip {length} cm long. The ends need trimming by {b} mm each. '
                    'How many millimetres of strip will remain? Show your working.')
        answer = 10*length-trim
        display = f'{answer} mm'
        steps = [f'{length} cm × 10 = {10*length} mm.',f'{10*length} − 2 × {b} = {answer} mm.']
        rubric = ['M1 for expressing the strip and both trimmings in consistent units.',
                  'A1 for the correct remaining length in millimetres from a valid method.']
    else:
        unit = 25*a+5*b
        question = (f'A club has a £20 repair budget. Three identical replacement clips cost {money(unit)} each. '
                    'How much can the club still spend? Show the calculation.')
        answer = 2000-3*unit
        display = money(answer)
        steps = [f'Three clips cost 3 × {money(unit)} = {money(3*unit)}.',
                 f'£20.00 − {money(3*unit)} = {display}.']
        rubric = ['M1 for subtracting the cost of three clips from the starting budget, or an equivalent method.',
                  'A1 for the correct balance from a valid method.']
    if not validate(skill,a,b,answer) or len(rubric)!=2:
        raise ValueError('Mathematical validation failed')
    return dict(label='Original practice · teacher review',unit='M1',tier='Foundation',skill=skill,
        question=question,solution=steps,answer=display,marks=2,rubric=rubric,mode=mode,
        difficulty='Standard (author estimate)',calculator='Permitted',spec=f"{SPEC}, p. {refs[0]['spec_page']}",
        validation='Inverse arithmetic and two-mark allocation checked',
        sources=[dict(id=r['id'],year=r['year'],series=r['series'],num=r['num'],part=r['part'],
                      page=r['page'],scheme_page=r['scheme_page']) for r in refs])
