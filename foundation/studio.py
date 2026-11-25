"""Original Foundation practice families; specification and source evidence stay distinct."""
import random
import sqlite3
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path
from . import contextual

# family: label, origin unit, exact skill ID, supported units
FAMILIES = {
    'percent': ('Percentage of an amount', 'M1', 'percentage', ('M1','M2','M5','M6')),
    'fraction': ('Fraction of an amount', 'M1', 'fractions', ('M1','M2','M5','M6')),
    'equation': ('One-variable linear equation', 'M1', 'equations', ('M1','M2','M5','M6')),
    'rounding': ('Rounding to a multiple', 'M1', 'rounding', ('M1','M2','M5','M6')),
    'area': ('Rectangle area', 'M1', 'area', ('M1','M2','M5','M6')),
    'hcf': ('Highest common factor', 'M2', 'm2-factors', ('M2','M6')),
    'lcm': ('Lowest common multiple', 'M2', 'm2-factors', ('M2','M6')),
    'midpoint': ('Midpoint of a segment', 'M2', 'm2-midpoint-length', ('M2','M6')),
    'ratio': ('Sharing in a ratio', 'M5', 'm5-ratio', ('M5','M6')),
    'sequence': ('Arithmetic sequence', 'M5', 'm5-sequences', ('M5','M6')),
    'binary': ('Binary to decimal', 'M6', 'm6-binary', ('M6',)),
    'nth-term': ('Linear nth term', 'M6', 'm6-nth-term', ('M6',)),
    'indices': ('Product of powers', 'M6', 'm6-algebra-indices', ('M6',)),
}
FAMILIES.update(contextual.FAMILIES)
UNITS = ('M1','M2','M5','M6')
DIFFICULTIES = ('easy','standard','challenge')


def skill_id(unit, origin, skill):
    return skill if unit == origin else f'{unit.lower()}-from-{origin.lower()}-{skill}'


def connect(path):
    if not Path(path).is_file():
        raise FileNotFoundError(path)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db


def evidence(db, unit, family):
    label, origin, skill, units = FAMILIES[family]
    if unit not in units:
        raise ValueError('Family is not enabled for this unit')
    sid = skill_id(unit, origin, skill)
    row = db.execute('SELECT id,label,page FROM skills WHERE id=? AND unit=?',(sid,unit)).fetchone()
    if not row:
        raise ValueError('Curriculum skill missing; restore the current checkpoint')
    refs = db.execute('''SELECT q.id,d.unit,d.year,d.series,d.component,q.num,q.part,q.page,q.scheme_page,q.marks
      FROM questions q JOIN documents d ON d.sha=q.paper
      JOIN pairs p ON p.paper=q.paper AND p.scheme=q.scheme
      JOIN postings t ON t.qid=q.id AND t.unit=d.unit AND t.term='*'
      WHERE q.status='verified' AND p.status='paired' AND q.skill=? AND d.unit=?
      ORDER BY d.year DESC,q.id LIMIT 3''',(sid,unit)).fetchall()
    return dict(skill=sid,skill_label=row['label'],spec_page=row['page'],
                evidence_level='related-skill-source-checked' if refs else 'specification-only',
                sources=[dict(r) for r in refs])


def catalog(path, unit):
    if unit not in UNITS: raise ValueError('Foundation unit required')
    db=connect(path)
    try:
        return [dict(family=k,label=v[0],**evidence(db,unit,k)) for k,v in FAMILIES.items()
                if unit in v[3] and db.execute('SELECT 1 FROM skills WHERE id=? AND unit=?',
                    (skill_id(unit,v[1],v[2]),unit)).fetchone()]
    finally: db.close()


def build(family, a, b, c):
    """Return original prompt, canonical answer, steps, proposed per-mark rubric."""
    if family in contextual.FAMILIES:
        return contextual.build(family,a,b,c)
    if family == 'percent':
        p,total=5*a,20*b; ans=p*total//100
        return f'Find {p}% of {total}.',ans,[f'{p}/100 x {total} = {ans}.'],['M1: multiply by the percentage as a fraction or decimal.','A1: correct amount.']
    if family == 'fraction':
        n,d=a,a+c; total=d*b; ans=n*b
        return f'Find {n}/{d} of {total}.',ans,[f'{total} / {d} = {b}.',f'{b} x {n} = {ans}.'],['M1: divide by denominator and multiply by numerator, or equivalent.','A1: correct amount.']
    if family == 'equation':
        rhs=a*b+c
        return f'Solve {a}x + {c} = {rhs}.',b,[f'{a}x = {rhs} - {c} = {a*b}.',f'x = {a*b} / {a} = {b}.'],['M1: isolate the variable term correctly.','A1: correct value of x.']
    if family == 'rounding':
        base=10 if c%2 else 100; n=base*a+b; ans=((n+base//2)//base)*base
        return f'Round {n} to the nearest {base}.',ans,[f'{n} lies between {(n//base)*base} and {(n//base+1)*base}; round to {ans}.'],['B1: correct rounded integer.']
    if family == 'area':
        ans=a*b
        return f'A rectangle measures {a} cm by {b} cm. Find its area in cm^2.',ans,[f'Area = {a} x {b} = {ans} cm^2.'],['M1: multiply length by width.','A1: correct area in square centimetres.']
    if family in ('hcf','lcm'):
        x,y=a*c,b*c; ans=gcd(x,y) if family=='hcf' else lcm(x,y)
        if family=='hcf':
            steps=[f'Common factors of {x} and {y} include '+', '.join(str(i) for i in range(1,ans+1) if x%i==y%i==0)+'.',f'Greatest common factor = {ans}.']
            rubric=['M1: identify common factors or use a valid gcd method.','A1: greatest common factor.']
        else:
            steps=[f'HCF of {x} and {y} is {gcd(x,y)}.',f'LCM = {x} x {y} / {gcd(x,y)} = {ans}.']
            rubric=['M1: use a valid common multiple or prime factor method.','A1: least positive common multiple.']
        return f'Find the {family.upper()} of {x} and {y}.',ans,steps,rubric
    if family=='midpoint':
        x,y=a-c,b-c; u,v=a+c,b+c
        return f'Find the midpoint of ({x}, {y}) and ({u}, {v}).',(a,b),[f'x = ({x} + {u}) / 2 = {a}.',f'y = ({y} + {v}) / 2 = {b}.'],['M1: average the corresponding coordinates.','A1: both coordinates correct in order.']
    if family=='ratio':
        total=(a+b)*c
        return f'Share {total} counters in the ratio {a}:{b}. Give both shares in order.',(a*c,b*c),[f'{a} + {b} = {a+b} parts; each part = {total} / {a+b} = {c}.',f'Shares are {a*c} and {b*c}.'],['M1: calculate the value of one ratio part, or equivalent.','A1: both shares correct and in order.']
    if family=='sequence':
        terms=[a+b*i for i in range(4)]; ans=(a+4*b,a+5*b)
        return 'Write the next two terms of '+', '.join(map(str,terms))+', ... assuming a constant difference.',ans,[f'The common difference is {b}.',f'Add {b} twice: {ans[0]}, {ans[1]}.'],['B1: first missing term correct.','B1: second missing term correct.']
    if family=='binary':
        n=a*b+c; digits=format(n,'b'); powers=[2**i for i,d in enumerate(reversed(digits)) if d=='1']
        return f'Convert the binary number {digits} to decimal (base 10).',n,['Add the place values of the 1 bits: '+' + '.join(map(str,powers))+f' = {n}.'],['M1: use binary place values correctly.','A1: correct decimal integer.']
    if family=='nth-term':
        terms=[a+b*i for i in range(4)]; k=a-b; ans=(b,k)
        return 'Find an expression for the nth term of '+', '.join(map(str,terms))+', ... assuming a constant difference.',ans,[f'The common difference is {b}, so start with {b}n.',f'At n = 1 the required value is {a}; adjust by {k}.'],['M1: identify the correct coefficient of n.','A1: correct complete linear expression.']
    if family=='indices':
        return f'Write (x^{a}) * (x^{b}) as a single power of x.',a+b,[f'For a common base, add the exponents: {a} + {b} = {a+b}.'],['B1: correct single power of x.']
    raise ValueError('Unknown family')


def validate(family,a,b,c,ans):
    """Independent inverse checks, enumeration and place-value reconstruction."""
    if family in contextual.FAMILIES: return contextual.validate(family,a,b,c,ans)
    if family=='percent': return Fraction(ans,20*b)==Fraction(a,20)
    if family=='fraction': return Fraction(ans,(a+c)*b)==Fraction(a,a+c)
    if family=='equation': return a*ans+c==a*b+c
    if family=='rounding':
        base=10 if c%2 else 100; n=base*a+b
        return ans%base==0 and -base//2<=n-ans<base//2
    if family=='area': return ans>0 and sum([a]*b)==ans
    if family=='hcf':
        x,y=a*c,b*c
        return ans==max(i for i in range(1,min(x,y)+1) if x%i==y%i==0)
    if family=='lcm':
        x,y=a*c,b*c
        return ans==next(i for i in range(x,x*y+1,x) if i%y==0)
    if family=='midpoint': return tuple(2*t for t in ans)==(a-c+a+c,b-c+b+c)
    if family=='ratio': return len(ans)==2 and sum(ans)==(a+b)*c and ans[0]*b==ans[1]*a
    if family=='sequence': return ans[0]-(a+3*b)==b and ans[1]-ans[0]==b
    if family=='binary':
        digits=format(a*b+c,'b'); result=0
        for d in digits: result=2*result+int(d)
        return ans==result
    if family=='nth-term': return ans[0]==b and all(ans[0]*n+ans[1]==a+b*(n-1) for n in range(1,6))
    if family=='indices': return 2**ans==2**a*2**b
    return False


def display(family,answer):
    if family in contextual.FAMILIES: return contextual.display(family,answer)
    if family=='nth-term':
        m,k=answer
        return f'{m}n'+(f' + {k}' if k>0 else f' - {-k}' if k<0 else '')
    if family=='indices': return f'x^{answer}'
    if family=='midpoint': return f'({answer[0]}, {answer[1]})'
    if isinstance(answer,tuple): return ', '.join(map(str,answer))
    return str(answer)+(' cm^2' if family=='area' else '')


def generate(path,unit,family,difficulty='standard',count=1,seed=None):
    if unit not in UNITS or family not in FAMILIES or difficulty not in DIFFICULTIES:
        raise ValueError('Unsupported unit, family or difficulty')
    if type(count) is not int or not 1<=count<=10: raise ValueError('Choose 1 to 10 questions')
    if unit not in FAMILIES[family][3]: raise ValueError('Family is not enabled for this unit')
    db=connect(path)
    try: meta=evidence(db,unit,family)
    finally: db.close()
    rng=random.Random(seed) if seed is not None else random.SystemRandom()
    lo,hi={'easy':(2,6),'standard':(4,12),'challenge':(8,18)}[difficulty]
    questions=[]; seen=set()
    for _ in range(500):
        a,b,c=(rng.randint(lo,hi) for _ in range(3))
        q,ans,steps,rubric=build(family,a,b,c)
        if q in seen: continue
        if not validate(family,a,b,c,ans): raise ValueError('Mathematical validation failed')
        seen.add(q)
        questions.append(dict(label=FAMILIES[family][0]+' - original practice',unit=unit,tier='Foundation',
            family=family,question=q,answer=display(family,ans),solution=steps,rubric=rubric,marks=len(rubric),
            diagram=contextual.diagram(family,a,b,c),
            mode='local',difficulty=difficulty+' (parameter range; not calibrated)',calculator='Not required by this template',
            spec=f'CCEA GCSE Mathematics (2017), section 3.1, p. {meta["spec_page"]}',
            validation='Independent numeric check passed; wording and proposed rubric require teacher review',**meta))
        if len(questions)==count: return questions
    raise ValueError('Could not generate enough distinct questions; reduce count')
