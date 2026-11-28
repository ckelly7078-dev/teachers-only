"""Exact checks on structured working for three specific AS1 Tier 3 designs.

Inputs are mathematical observations supplied by an existing parser/reviewer, not
raw student work. Unimplemented methods stay uncertain; no score is released.
"""
import re
from fractions import Fraction
from collections import Counter
from active_difficulty import require
from engine_fm17d import reconcile_proposal


def rational(value):
    require(isinstance(value,str) and re.fullmatch(r'-?\d{1,12}(?:/[1-9]\d{0,11})?',value) is not None,'Use bounded exact rational strings')
    return Fraction(value)


def pair(values):
    require(isinstance(values,list) and len(values)==2,'Expected pair')
    return tuple(rational(v) for v in values)


def matrix(values, rows, cols):
    require(isinstance(values,list) and len(values)==rows and all(isinstance(r,list) and len(r)==cols for r in values),'Incorrect matrix shape')
    return [list(map(rational,r)) for r in values]


def obs(i, status, text):
    return {'criterion_id':f'c{i}','status':status,'evidence':text}


def flag(value):
    return 'met' if value else 'not_met'


def check_work(engine,item_id,*,mode,item_fingerprint,work):
    context=engine.marking_context(item_id,mode=mode,item_fingerprint=item_fingerprint)
    p=engine.bank.items[item_id]['payload']; path=p['path']; q=p['question_latex']
    require(p['tier']==3 and path in ('root-sum-product','angle-units','matrix-products'),'Structured checker unavailable for this design')
    require(isinstance(work,dict),'Structured working required')
    if path=='root-sum-product':
        require(set(work)=={'method','operands','answer'},'Invalid root working')
        m=re.fullmatch(r'Without solving the equation \$(\d+) x\^\{2\} - (\d+) x \+ (\d+)\$ = 0, calculate the sum and product of its roots\.',q)
        require(m is not None,'Unsupported root prompt revision')
        a,b,c=map(int,m.groups()); expected=(Fraction(b,a),Fraction(c,a))
        require(tuple(map(rational,p['facts']))==expected,'Inconsistent root facts')
        method=work['method']; operands=work['operands']
        if method in ('ratio','monic'):
            require(isinstance(operands,list) and len(operands)==2,'Both ratios required')
            pairs=tuple(pair(x) for x in operands)
            valid=(pairs==((b,a),(c,a))) if method=='ratio' else (pairs==((expected[0],1),(expected[1],1)))
            method_status=flag(valid); detail='Both signed ratios match the original coefficients or the monic form.' if valid else 'The submitted coefficient operands do not match the stated method.'
        elif method in ('other','none'):
            require(operands is None,'Unrecognized method operands')
            method_status='uncertain' if method=='other' else 'not_met'; detail='Method not covered by the checker.' if method=='other' else 'No method supplied in the structured record.'
        else:
            raise ValueError('Unknown method')
        ans=pair(work['answer']); decisions=[obs(1,method_status,detail),obs(2,flag(ans==expected),'Exact sum and product compared with independent coefficient ratios.')]
    elif path=='angle-units':
        require(set(work)=={'answer_degrees'},'Invalid angle working')
        m=re.fullmatch(r'Convert the signed angle \$- (?:([0-9]+) \\pi|\\frac\{([0-9]+) \\pi\}\{([0-9]+)\})\$ radians into degrees without normalizing it\.',q)
        require(m is not None,'Unsupported angle prompt revision')
        n,num,den=m.groups(); expected=-180*(Fraction(int(n)) if n else Fraction(int(num),int(den)))
        require(rational(p['facts'][0])==expected,'Inconsistent angle facts')
        decisions=[obs(1,flag(rational(work['answer_degrees'])==expected),'Compared exact signed degrees without reduction modulo a turn.')]
    else:
        require(set(work)=={'dimensions','method','terms','answer'},'Invalid matrix working')
        blocks=re.findall(r'\\begin\{matrix\}(.*?)\\end\{matrix\}',q)
        require(len(blocks)==2,'Unsupported matrix prompt revision')
        a,b=([[rational(x.strip()) for x in row.split('&')] for row in block.split(r'\\')] for block in blocks)
        require(len(a)==2 and all(len(r)==3 for r in a) and len(b)==3 and all(len(r)==2 for r in b),'Unexpected source dimensions')
        expected=[[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(2)] for i in range(2)]
        require(matrix(p['facts'][0]['matrix'],2,2)==expected,'Inconsistent matrix facts')
        dims=pair(work['dimensions']); method=work['method']; terms=work['terms']
        if method=='row_column':
            require(isinstance(terms,list) and len(terms)==2 and all(isinstance(r,list) and len(r)==2 for r in terms),'Four dot products required')
            valid=True
            for i,j in ((0,0),(0,1),(1,0),(1,1)):
                factors=terms[i][j]; require(isinstance(factors,list) and len(factors)==3,'Three factor pairs required')
                actual=Counter(tuple(sorted(pair(x))) for x in factors)
                wanted=Counter(tuple(sorted((a[i][k],b[k][j]))) for k in range(3))
                valid &= actual==wanted
            status=flag(valid); detail='Compared the four row-column factor multisets; term order and scalar factor order may vary.'
        elif method in ('other','none'):
            require(terms is None,'Unrecognized matrix method terms')
            status='uncertain' if method=='other' else 'not_met'; detail='Other valid methods require interpretation.' if method=='other' else 'No method supplied in the structured record.'
        else:
            raise ValueError('Unknown method')
        ans=matrix(work['answer'],2,2)
        decisions=[obs(1,flag(dims==(2,2)),'Compared output dimensions.'),obs(2,status,detail),obs(3,flag(ans==expected),'Independently calculated all four exact product entries.')]
    expected_types={'root-sum-product':['M','A'],'angle-units':['A'],'matrix-products':['A','M','A']}[path]
    require([r['type'] for r in context['criteria']]==expected_types and all(r['marks']==1 for r in context['criteria']),'Unsupported rubric revision')
    result=reconcile_proposal(context,decisions)
    result['basis']='exact_checks_on_supplied_structured_observations'
    return result
