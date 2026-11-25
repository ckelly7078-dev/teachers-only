"""Original multi-part Foundation questions with dimension-driven mathematical diagrams.

All numbers and diagram labels derive from one parameter set. No model or source
text is required. Proposed rubrics are not official CCEA marking schemes.
"""
from fractions import Fraction
from math import isqrt
from . import geometry

FAMILIES = {
    'discount-budget': ('Discount and delivery budget', 'M1', 'finance', ('M1','M2','M5','M6')),
    'l-shape': ('Composite floor area and cost', 'M1', 'area', ('M1','M2','M5','M6')),
    'trapezium': ('Trapezium area and cost', 'M2', 'm2-plane-area', ('M2','M6')),
    'pythagoras': ('Right triangle and length cost', 'M2', 'm2-pythagoras', ('M2','M6')),
    'map-scale': ('Map scale and return journey', 'M5', 'm5-scale', ('M5','M6')),
    'expected-frequency': ('Probability and expected frequency', 'M5', 'm5-expectation', ('M5','M6')),
    'gradient': ('Gradient and intercept', 'M2', 'm2-gradient', ('M2','M6')),
}


def cash(pence):
    return f'{pence//100}.{pence%100:02d}'


def build(family,a,b,c):
    if family=='discount-budget':
        price=2000+100*a*b; p=5*c; saving=price*p//100; delivery=100*b
        budget=price+delivery+100*a; paid=price-saving+delivery; left=budget-paid
        return (f'A club has a budget of £{cash(budget)}. A kit costs £{cash(price)} before a {p}% discount. Delivery costs £{cash(delivery)} and is not discounted. (a) Find the total paid including delivery. (b) Find the money left in the budget.',
                (paid,left),[f'Discount = {p}/100 x £{cash(price)} = £{cash(saving)}.',f'Amount paid = £{cash(price)} - £{cash(saving)} + £{cash(delivery)} = £{cash(paid)}.',f'Money left = £{cash(budget)} - £{cash(paid)} = £{cash(left)}.'],
                ['(a) M1: calculate the discount or apply the remaining percentage.','(a) M1: include delivery after discount.','(a) A1: correct total paid.','(b) A1: correct balance; follow through a valid subtraction using part (a).'])
    if family=='l-shape':
        w,h=a+b,b+c; area=w*h-b*c; rate=c+2; cost=area*rate
        return (f'An L-shaped floor is made by removing a {b} m by {c} m corner from a {w} m by {h} m rectangle (see diagram). Flooring costs £{rate} per square metre. (a) Find the floor area. (b) Find the flooring cost, ignoring waste.',(area,cost),
                [f'Outer area = {w} x {h} = {w*h} m^2.',f'Remove {b} x {c} = {b*c} m^2; floor area = {area} m^2.',f'Cost = {area} x £{rate} = £{cost}.'],
                ['(a) M1: calculate outer and removed areas, or split the L shape into rectangles.','(a) M1: subtract the removed area, or add non-overlapping areas.','(a) A1: correct floor area.','(b) A1: correct cost; follow through a valid multiplication of part (a).'])
    if family=='trapezium':
        top=2*a; bottom=2*(a+b); height=c; area=(top+bottom)*height//2; rate=b+1
        return (f'A trapezium-shaped garden has parallel sides {top} m and {bottom} m and perpendicular height {height} m (see diagram). Turf costs £{rate} per square metre. (a) Find its area. (b) Find the turf cost, ignoring waste.',(area,area*rate),
                [f'Area = ({top} + {bottom}) x {height} / 2 = {area} m^2.',f'Cost = {area} x £{rate} = £{area*rate}.'],
                ['(a) M1: add the two parallel sides and multiply by perpendicular height.','(a) M1: divide by 2 or use an equivalent decomposition.','(a) A1: correct area.','(b) A1: correct cost; follow through a valid multiplication of part (a).'])
    if family=='pythagoras':
        x,y,length=geometry.triangle_sides(a,b,c); rate=b+c
        return (f'A rectangular frame is {x} m wide and {y} m high. A straight brace runs from one corner to the opposite corner (see diagram). The brace material costs £{rate} per metre. (a) Find the length of the brace. (b) Find the material cost.',(length,length*rate),
                [f'Brace length squared = {x}^2 + {y}^2 = {x*x+y*y}.',f'Length = sqrt({x*x+y*y}) = {length} m.',f'Cost = {length} x £{rate} = £{length*rate}.'],
                ['(a) M1: use Pythagoras with the two perpendicular sides.','(a) M1: take the positive square root of their squared sum.','(a) A1: correct length.','(b) A1: correct cost; follow through a valid multiplication of part (a).'])
    if family=='map-scale':
        scale=c; outward=(a+b)*scale
        return (f'On a map, 1 cm represents {scale} km. A route consists of two consecutive legs measuring {a} cm and {b} cm on the map. (a) Find the real outward distance in kilometres. (b) Find the total distance if the traveller returns along the same route.',(outward,2*outward),
                [f'Map distance = {a} + {b} = {a+b} cm.',f'Outward distance = {a+b} x {scale} = {outward} km.',f'Return journey total = 2 x {outward} = {2*outward} km.'],
                ['(a) M1: add map distances or convert each leg separately.','(a) A1: correct outward distance in kilometres.','(b) A1: correct return journey total; follow through twice part (a).'])
    if family=='expected-frequency':
        total=a+b+c; trials=total*c; prob=Fraction(b+c,total); expected=(b+c)*c
        return (f'A bag contains {a} red, {b} blue and {c} green counters. On each draw every counter is equally likely to be selected; the counter is replaced after each draw. (a) Find the probability of not drawing red. Give a fraction in simplest form. (b) In {trials} draws, how many non-red counters would you expect?',(prob,expected),
                [f'Non-red counters = {b} + {c} = {b+c}; total = {total}.',f'Probability = {b+c}/{total} = {prob}.',f'Expected frequency = {trials} x {prob} = {expected}.'],
                ['(a) M1: use non-red count over total, or one minus probability of red.','(a) A1: correct probability in simplest form.','(b) M1: multiply number of draws by the probability.','(b) A1: correct expected frequency; follow through a valid probability from part (a).'])
    if family=='gradient':
        rise=a; run=b; intercept=c; m=Fraction(rise,run)
        return (f'A straight line passes through (0, {intercept}) and ({run}, {intercept+rise}). (a) Find its gradient. Give an exact answer, simplifying any fraction. (b) State the y-coordinate where it crosses the y-axis.',(m,intercept),
                [f'Rise = {intercept+rise} - {intercept} = {rise}; run = {run} - 0 = {run}.',f'Gradient = {rise}/{run} = {m}.',f'When x = 0, y = {intercept}.'],
                ['(a) M1: divide change in y by change in x.','(a) A1: correct gradient in simplest form.','(b) B1: correct y-intercept coordinate.'])
    raise ValueError('Unknown contextual family')


def validate(family,a,b,c,answer):
    if not isinstance(answer,tuple) or len(answer)!=2: return False
    x,y=answer
    if family=='discount-budget':
        price=2000+100*a*b; delivery=100*b; budget=price+delivery+100*a
        return Fraction(x-delivery,price)==1-Fraction(c,20) and x+y==budget
    if family=='l-shape': return x==a*(b+c)+b*b and y==sum([x]*(c+2))
    if family=='trapezium': return x==2*a*c+b*c and y==sum([x]*(b+1))
    if family=='pythagoras':
        w,h,_=geometry.triangle_sides(a,b,c)
        return x>0 and x==isqrt(w*w+h*h) and x*x==w*w+h*h and y==sum([x]*(b+c))
    if family=='map-scale': return Fraction(x,c)==a+b and y-x==x
    if family=='expected-frequency': return 1-x==Fraction(a,a+b+c) and Fraction(y,(a+b+c)*c)==x
    if family=='gradient': return y==c and x*b+y==c+a
    return False


def display(family,answer):
    x,y=answer
    if family=='discount-budget': return f'(a) £{cash(x)}; (b) £{cash(y)}'
    if family in ('l-shape','trapezium'): return f'(a) {x} m^2; (b) £{y}'
    if family=='pythagoras': return f'(a) {x} m; (b) £{y}'
    if family=='map-scale': return f'(a) {x} km; (b) {y} km'
    return f'(a) {x}; (b) {y}'


def diagram(family,a,b,c):
    return geometry.diagram(family,a,b,c)
