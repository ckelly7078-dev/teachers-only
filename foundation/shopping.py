"""Original three-part shopping questions; exact money arithmetic in integer pence."""
from fractions import Fraction

FAMILIES = {'shopping-discount': ('Shopping discount, sale price and budget', 'M1', 'finance', ('M1','M2','M5','M6'))}


def cash(pence):
    return f'£{pence//100}.{pence%100:02d}'


def build(a,b,c):
    price=2000*a; percent=5*b; saving=price*percent//100
    sale=price-saving; budget=sale+100*c
    question=(f'A sports shop sells a bicycle for {cash(price)}. During a sale, the price is reduced by {percent}%. '
              f'(a) Calculate the amount of the reduction. (b) Calculate the sale price of the bicycle. '
              f'(c) A customer has {cash(budget)}. How much money will they have left after buying the bicycle?')
    return question,(saving,sale,budget-sale),[
        f'(a) {percent}/100 × {cash(price)} = {cash(saving)}.',
        f'(b) {cash(price)} − {cash(saving)} = {cash(sale)}.',
        f'(c) {cash(budget)} − {cash(sale)} = {cash(budget-sale)}.'],[
        '(a) M1: calculate the discount using a fraction, decimal or equivalent percentage method.',
        '(a) A1: correct amount of the reduction.',
        '(b) A1: correct sale price; follow through a valid subtraction using part (a), or calculate directly.',
        '(c) A1: correct remaining money; follow through a valid subtraction using part (b).']


def validate(a,b,c,answer):
    if not isinstance(answer,tuple) or len(answer)!=3 or any(type(x) is not int for x in answer): return False
    discount,paid,remaining=answer
    original=2000*a
    budget=original*(20-b)//20+100*c
    return discount>0 and paid>0 and remaining>=0 and Fraction(discount,original)==Fraction(b,20) and discount+paid==original and paid+remaining==budget


def display(answer):
    return '; '.join(f'({part}) {cash(value)}' for part,value in zip('abc',answer))
