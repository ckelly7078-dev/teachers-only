"""Designed cognitive demand, not empirical grade boundaries.

Used by the structured Studio only. The legacy direct-family generator remains
compatible. Original base answers are validated before this adapter is called.
Hard extensions use explicit independent inverse/reconstruction checks.
"""
from fractions import Fraction
from math import gcd,lcm
from . import composite, geometry, studio

LEVELS={'easy':'Easy — guided recall and direct calculation',
        'standard':'Medium — independent application',
        'challenge':'Hard — linked reasoning and problem solving'}
HINTS={
 'percent':'Convert the percentage to a fraction out of 100, then multiply.',
 'fraction':'Divide by the denominator first, then multiply by the numerator.',
 'equation':'Subtract the constant from both sides before dividing by the coefficient.',
 'rounding':'Identify the two neighbouring multiples, then choose the nearer one; round a halfway value up.',
 'area':'Use area = length × width.',
 'hcf':'List factors of each number and look for the largest common factor.',
 'lcm':'List multiples of each number and look for the first positive common multiple.',
 'midpoint':'Average the two x-coordinates, then average the two y-coordinates.',
 'ratio':'Add the ratio parts and divide the total by that number first.',
 'sequence':'Find the difference between consecutive terms and keep adding it.',
 'binary':'Use place values 1, 2, 4, 8, ... starting from the right.',
 'nth-term':'Start with the common difference times n, then adjust for the first term.',
 'indices':'When multiplying powers of the same base, add the exponents.',
}


def check(ok):
    if not ok: raise ValueError('Difficulty extension validation failed')


def update(row,q,ans,steps,rubric,features):
    row.update(question=q,answer=ans,solution=steps,rubric=rubric,marks=len(rubric),difficulty_features=features)


def easy_context(row,f,a,b,c,raw):
    # Each easy question contains one direct task; the harder contexts and
    # later subparts are reserved for medium/hard.
    x=raw[0]
    if f=='shopping-discount':
        p,total=5*b,20*a; q=f'A bicycle costs £{total}. Find the {p}% discount. Use percentage / 100 × price.'; ans=f'£{x/100:.2f}'; step=f'{p}/100 × £{total} = {ans}.'
    elif f=='discount-budget':
        price=20+a*b; p=5*c; saving=price*Fraction(p,100); q=f'A kit costs £{price}. Find its price after a {p}% discount. Subtract the discount from the original price.'; ans=f'£{float(price-saving):.2f}'; step=f'£{price} − £{float(saving):.2f} = {ans}.'; check((price-saving)*100==x-100*b)
    elif f=='trapezium':
        q=f'Find the area of the trapezium in the diagram. Use area = (sum of parallel sides) × perpendicular height ÷ 2.'; ans=f'{x} m^2';step=f'({2*a} + {2*(a+b)}) × {c} ÷ 2 = {ans}.'
    elif f=='pythagoras':
        w,h,z=geometry.triangle_sides(a,b,c); q='Find the length of the diagonal brace in the rectangular frame. Use Pythagoras: diagonal squared = width squared + height squared.';ans=f'{x} m';step=f'sqrt({w}^2 + {h}^2) = {ans}.';check(z==x)
    elif f=='map-scale':
        q=f'On a map, 1 cm represents {c} km. A route is {a+b} cm long on the map. Find the real distance. Multiply the map length by the scale.';ans=f'{x} km';step=f'{a+b} × {c} = {ans}.'
    elif f=='expected-frequency':
        q=f'A bag contains {a} red, {b} blue and {c} green counters. One counter is drawn at random. Find the probability of not drawing red, as a simplified fraction. Use favourable outcomes / total outcomes.';ans=str(x);step=f'({b}+{c}) / ({a}+{b}+{c}) = {ans}.'
    elif f=='gradient':
        q=f'A straight line passes through (0, {c}) and ({b}, {c+a}). Find its gradient as a simplified fraction. Use change in y ÷ change in x.';ans=str(x);step=f'({c+a} − {c}) / {b} = {ans}.'
    else: raise ValueError('Missing guided family')
    update(row,q,ans,[step],['M1: use the stated method or a valid equivalent.','A1: correct final answer.'],'One direct task with a method cue; no dependent follow-up.')


def hard_basic(row,f,a,b,c,raw):
    # New contexts require interpreting or reversing a relationship, not
    # just repeating a direct computation with bigger numbers.
    if f=='percent':
        p=5*a; total=20*b; left=total-raw; pay=left+c; check(raw*100==p*total and pay-left==c)
        q=f'A jacket costs £{total}. Its price is reduced by {p}%. A customer has £{pay}. (a) Find the sale price. (b) Find how much money the customer has left.'
        ans=[f'£{left}',f'£{c}'];steps=[f'Discount = {p}/100 × {total} = £{raw}.',f'Sale price = {total} − {raw} = £{left}.',f'Balance = {pay} − {left} = £{c}.'];rub=[3,1]
    elif f=='fraction':
        total=(a+c)*b; rem=total-raw; check(Fraction(raw,total)==Fraction(a,a+c) and rem+raw==total)
        q=f'A tank holds {total} litres when full. {a}/{a+c} of the water is used. (a) Find the amount remaining. (b) Express the remaining amount as a fraction of the full tank, in simplest form.'
        ans=[f'{rem} litres',str(Fraction(rem,total))];steps=[f'Used = {a}/{a+c} × {total} = {raw} litres.',f'Remaining = {total} − {raw} = {rem} litres.',f'Fraction remaining = {rem}/{total} = {Fraction(rem,total)}.'];rub=[3,2]
    elif f=='equation':
        rhs=a*b+c; check((rhs-c)%a==0 and (rhs-c)//a==b)
        q=f'A group pays £{rhs} for a booking. There is one fixed booking charge of £{c}, then £{a} per person. (a) Form an equation in n, the number of people. (b) Solve it to find the number of people.'
        ans=[f'{a}n + {c} = {rhs}',str(b)];steps=[f'{a}n + {c} = {rhs}.',f'{a}n = {rhs-c}; n = {b}.'];rub=[2,2]
    elif f=='rounding':
        base=10 if c%2 else 100; n=base*a+b; rounded=raw; lo=rounded-base//2; hi=rounded+base//2-1; check(lo<=n<=hi and (lo+base//2)//base*base==rounded and (hi+base//2)//base*base==rounded)
        q=f'A whole-number attendance count is rounded to the nearest {base}, giving {rounded}. Use the usual rule that halfway values round up. (a) Find the smallest possible actual attendance. (b) Find the largest possible actual attendance.'
        ans=[str(lo),str(hi)];steps=[f'Half a rounding interval is {base//2}.',f'Smallest = {rounded} − {base//2} = {lo}.',f'Largest = {rounded} + {base//2} − 1 = {hi}.'];rub=[2,2]
    elif f=='area':
        area=a*b; perimeter=2*(a+b); check(area==raw and perimeter==a+b+a+b)
        q=f'A rectangular garden has area {area} m^2 and length {a} m. (a) Find its width. (b) Find the length of fencing needed around it, with a {min(3,c)} m gap for a gate.'
        gap=min(3,c);ans=[f'{b} m',f'{perimeter-gap} m'];steps=[f'Width = {area} ÷ {a} = {b} m.',f'Perimeter = 2 × ({a}+{b}) = {perimeter} m.',f'Fencing = {perimeter} − {gap} = {perimeter-gap} m.'];rub=[2,2]
    elif f=='hcf':
        x,y=a*c,b*c; n=raw;check(x%n==0 and y%n==0 and not any(x%i==y%i==0 for i in range(n+1,min(x,y)+1)))
        q=f'A teacher has {x} pencils and {y} pens. They make as many identical sets as possible, using every item. (a) Find the maximum number of sets. (b) Find the number of pencils and pens in each set.'
        ans=[str(n),f'{x//n} pencils and {y//n} pens'];steps=[f'HCF({x}, {y}) = {n}.',f'{x} ÷ {n} = {x//n}; {y} ÷ {n} = {y//n}.'];rub=[2,2]
    elif f=='lcm':
        x,y=a*c,b*c;n=raw;check(n%x==n%y==0 and not any(i%y==0 for i in range(x,n,x)))
        q=f'Two lights flash together now. One flashes every {x} seconds and the other every {y} seconds. (a) Find the time until they next flash together. (b) How many times will they flash together after now, up to and including {c*n} seconds from now?'
        ans=[f'{n} seconds',str(c)];steps=[f'LCM({x}, {y}) = {n} seconds.',f'{c*n} ÷ {n} = {c}.'];rub=[2,2]
    elif f=='midpoint':
        x,y=a-c,b-c;u,v=a+c,b+c;check((x+u,y+v)==(2*a,2*b))
        q=f'A line segment has endpoint ({x}, {y}) and midpoint ({a}, {b}). (a) Find the other endpoint. (b) Show that the midpoint of your two endpoints is ({a}, {b}).'
        ans=[f'({u}, {v})',f'({a}, {b})'];steps=[f'Other x = 2 × {a} − ({x}) = {u}; other y = 2 × {b} − ({y}) = {v}.',f'Check: ({x} + {u}) ÷ 2 = {a}; ({y} + {v}) ÷ 2 = {b}.'];rub=[3,1]
    elif f=='ratio':
        x,y=raw; total=x+y;check(x*b==y*a and total==(a+b)*c)
        q=f'Red and blue counters are in the ratio {a}:{b}. There are {x} red counters. (a) Find the total number of counters. (b) Find the fraction of all counters that are blue, in simplest form.'
        ans=[str(total),str(Fraction(y,total))];steps=[f'One ratio part = {x} ÷ {a} = {c}.',f'Blue = {b} × {c} = {y}; total = {total}.',f'Fraction = {y}/{total} = {Fraction(y,total)}.'];rub=[3,2]
    elif f=='sequence':
        # M5 permits number patterns; avoid requiring the M6 nth-term method.
        first=a; end=a+5*b;check((end-first)%5==0 and (end-first)//5==b)
        q=f'A sequence has a constant difference. Its first term is {first} and sixth term is {end}. (a) Find the common difference. (b) Find the third and seventh terms.'
        ans=[str(b),f'{a+2*b}, {a+6*b}'];steps=[f'There are 5 equal steps; ({end} − {first}) ÷ 5 = {b}.',f'Third = {a} + 2 × {b} = {a+2*b}; seventh = {a} + 6 × {b} = {a+6*b}.'];rub=[2,2]
    elif f=='binary':
        n=raw; m=c; total=n+m;check(int(format(total,'b'),2)-int(format(n,'b'),2)==m)
        q=f'Two counters show binary numbers {n:b} and {m:b}. (a) Convert both numbers to decimal. (b) Add the decimal values and express the sum in binary.'
        ans=[f'{n}, {m}',format(total,'b')];steps=[f'Binary place values give {n} and {m}.',f'{n} + {m} = {total}; converting back gives {total:b}.'];rub=[2,3]
    elif f=='nth-term':
        m,k=raw; target=a+b*(c+2); index=c+3;check(m*index+k==target and (target-k)%m==0)
        terms=', '.join(str(a+i*b) for i in range(4)); expression=f'{m}n'+(f' + {k}' if k>0 else f' − {-k}' if k<0 else '')
        q=f'The sequence {terms}, ... has a constant difference. (a) Find its nth term. (b) Which term of the sequence is {target}?'
        ans=[expression,str(index)];steps=[f'Common difference {m}; first term adjustment {k}; nth term = {expression}.',f'{expression} = {target}, so n = {index}.'];rub=[2,2]
    elif f=='indices':
        n=raw;target=n+c;check(2**a*2**b*2**c==2**target)
        q=f'(a) Simplify (x^{a}) × (x^{b}) as one power of x. (b) Find the positive integer k for which (x^{a}) × (x^{b}) × (x^k) = x^{target} for all x.'
        ans=[f'x^{n}',str(c)];steps=[f'Add the known exponents: {a}+{b}={n}.',f'{n}+k={target}, so k={c}.'];rub=[1,2]
    else:raise ValueError('Missing hard basic family')
    methods={
      'percent': [['calculate discount', 'subtract discount from original price'],[]],
      'fraction': [['calculate amount used','subtract from total'],['write remaining over total and simplify']],
      'equation': [['identify fixed charge and variable cost'],['isolate n correctly']],
      'rounding': [['subtract half the rounding interval'],['identify last integer below the upper midpoint']],
      'area': [['divide area by length'],['calculate perimeter and subtract gate width']],
      'hcf': [['use a valid HCF method'],['divide both totals by number of sets']],
      'lcm': [['use a valid LCM method'],['divide time interval by common flash interval']],
      'midpoint': [['double midpoint x and subtract known x','double midpoint y and subtract known y'],[]],
      'ratio': [['find the value of one part','find blue count and add both shares'],['express blue count over total and simplify']],
      'sequence': [['divide difference between given terms by five'],['use the common difference to reach both requested terms']],
      'binary': [['use binary place values'],['add decimal values','convert sum to binary']],
      'nth-term': [['identify common difference and adjust for first term'],['solve the equation for the term index']],
      'indices': [[],['equate exponents and isolate k']],
    }[f]
    rubric=[]
    for i,n in enumerate(rub):
        tag=f'({chr(97+i)}) '
        check(len(methods[i])==n-1)
        rubric.extend(tag+'M1: '+method+' or equivalent.' for method in methods[i])
        rubric.append(tag+('B1: show both coordinate averages equal the given midpoint.' if f=='midpoint' and i==1 else 'A1: '+ans[i]+'.'))
    update(row,q,'; '.join(f'({chr(97+i)}) {v}' for i,v in enumerate(ans)),steps,rubric,'Interpret or reverse the given relationship, then complete a linked calculation without a method cue.')


def hard_context(row,f,a,b,c,raw):
    # Add a dependent practical decision, using the base validated answers.
    x,y=raw[:2];letter='d' if f=='shopping-discount' else 'c'
    if f=='shopping-discount':
        balance=raw[2]; price=100*(c+2+a%5); lock=100*(2+b%5); answer=price+lock-balance;check(answer>0 and balance+answer==price+lock)
        question=f'The customer also wants a helmet costing £{price/100:.2f} and a lock costing £{lock/100:.2f}. How much more money is needed after buying the bicycle?'; value=f'£{answer/100:.2f}'; step=f'£{price/100:.2f} + £{lock/100:.2f} − £{balance/100:.2f} = {value}.'
    elif f=='discount-budget':
        extra=100*(c+1); check(y>=0); left=y-extra;check(left+extra==y)
        question=f'The club also pays a further £{extra/100:.2f} fee. Find the new budget balance (a negative balance means over budget).';value=f'£{left/100:.2f}' if left>=0 else f'−£{-left/100:.2f}';step=f'Balance after fee = {y/100:.2f} − {extra/100:.2f} = {value}.'
    elif f=='trapezium':
        pack=3+b%4; n=(x+pack-1)//pack;check((n-1)*pack<x<=n*pack)
        question=f'Instead of loose turf, a supplier sells whole rolls covering {pack} m^2 each. Offcuts can be reused. Find the minimum number of rolls needed.';value=f'{n} rolls';step=f'{x} ÷ {pack}; round up to {n} rolls.'
    elif f=='pythagoras':
        length=x; stock=3+c%4; n=(length+stock-1)//stock;check((n-1)*stock<length<=n*stock)
        question=f'The brace material is sold in whole {stock} m lengths. Pieces can be joined without any loss. Find the minimum number of stock lengths needed.';value=f'{n} lengths';step=f'{length} ÷ {stock}; round up to {n} lengths.'
    elif f=='map-scale':
        speed=2+c%4; time=Fraction(y,speed);check(time*speed==y)
        question=f'The traveller covers {speed} km per hour at a constant speed. Find the total travel time in hours as an exact number (a fraction is allowed).';value=f'{time} hours';step=f'{y} ÷ {speed} = {time} hours.'
    elif f=='expected-frequency':
        trials=(a+b+c)*c; red=trials-y;check(Fraction(red,trials)==Fraction(a,a+b+c))
        question=f'Find the expected number of red counters in the same {trials} draws.';value=str(red);step=f'{trials} − {y} = {red}.'
    elif f=='gradient':
        xx=b*2; yy=y+x*xx;check((yy-y)/xx==x)
        question=f'Find the y-coordinate on the same line when x = {xx}.';value=str(yy);step=f'y = {y} + ({x}) × {xx} = {yy}.'
    else: raise ValueError('Missing hard contextual family')
    method={'shopping-discount':'add both accessory prices and subtract remaining budget','discount-budget':'subtract the further fee from the remaining budget','trapezium':'divide the area by the coverage of one roll','pythagoras':'divide the brace length by the stock length','map-scale':'divide total distance by speed','expected-frequency':'subtract non-red expected frequency from total draws or use probability of red','gradient':'apply the gradient to the new x-coordinate and add the intercept'}[f]
    update(row,row['question']+f' ({letter}) '+question,row['answer']+f'; ({letter}) '+value,row['solution']+[step],row['rubric']+[f'({letter}) M1: {method}, or equivalent.',f'({letter}) A1: {value}; follow through a valid earlier result.'],'Multi-part application with a dependent interpretation or practical decision.')


def diagram_for(family,level,a,b,c,layout=None):
    layout=geometry.default_layout(a,b,c) if layout is None else layout
    if family=='l-shape':return composite.diagram(level,a,b,c,layout)
    return geometry.diagram(family,a,b,c,layout)


def adapt(row,level,a,b,c,layout=None):
    f=row['family'];layout=geometry.default_layout(a,b,c) if layout is None else layout
    if f=='l-shape':
        row.update(composite.question(level,a,b,c,layout)); row['label']='Composite floor area — original practice'
    else:
        raw=studio.build(f,a,b,c)[1]
        if not studio.validate(f,a,b,c,raw): raise ValueError('Base calculation invalid')
        if level=='easy':
            if f in HINTS:
                row['question']+=' Hint: '+HINTS[f];row['difficulty_features']='Guided method cue and direct calculation with smaller parameters.'
            else:easy_context(row,f,a,b,c,raw)
        elif level=='standard':row['difficulty_features']='Independent application of the selected skill without a method cue.'
        elif f in HINTS:hard_basic(row,f,a,b,c,raw)
        else:hard_context(row,f,a,b,c,raw)
        if f in geometry.FAMILIES:row['diagram']=diagram_for(f,level,a,b,c,layout)
    row['difficulty']=LEVELS[level]+' (designed estimate; not calibrated)'
    row['difficulty_level']=level
    row['validation']='Independent numeric check passed; designed difficulty and proposed marking scheme require teacher review'
    return row
