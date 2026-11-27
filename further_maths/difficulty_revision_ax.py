"""FM-16AX: design-specific provisional marking of complex polynomial roots."""
import importlib

BANKS = {
    'complex-discriminant': 'x', 'complex-quadratic': 'x',
    'conjugate-deduction': 'x', 'conjugate-factor': 'x',
    'solve-cubic': 'y', 'solve-quartic': 'y', 'verify-roots': 'z',
}
# Each entry describes a distinct mark requirement, not a mandated sequence of
# prose steps. Preserve the AH conjugate-factor challenge and its typed rubric.
DESIGNS = {
    'complex-discriminant': (
        ('A:Give the correct signed discriminant.',),
        ('A:Give both exact discriminants.',
         'R:Explain why equal middle coefficients do not imply equal discriminants, and correctly classify both quadratics.'),
        ('M:Calculate the discriminant using all three signed coefficients, including the nonmonic leading coefficient.',
         'A:Give the exact negative discriminant and classify the roots as two distinct non-real conjugates.'),
        ('M:Form the discriminant as a quadratic expression in k and impose strict negativity.',
         'A:Give the exact open interval and both repeated-root boundary values.'),
        ('M:Form both discriminants and their zero thresholds.',
         'R:Use the ordering of the thresholds to establish which equation can be non-real while the other is real.',
         'A:Give the exact interval with the lower endpoint excluded and upper endpoint included, identifying the repeated root at the upper endpoint.'),
        ('M:Obtain both discriminants as functions of h and k.',
         'R:Classify each quadratic by comparing h with its threshold, distinguishing all three root types.',
         'A:Give the exact common repeated-root parameter pair.',
         'R:Derive the region where exactly one discriminant is negative, including only the larger threshold and allowing an empty region when the thresholds coincide.',
         'R:Justify that the sign comparisons include both boundary curves and exhaust all real parameter pairs.')),
    'complex-quadratic': (
        ('A:Give both distinct imaginary roots with correct signs.',),
        ('R:Explain the two distinct imaginary square-root branches and why shifting preserves distinctness.',
         'A:Give the missing Cartesian root.'),
        ('M:Use the quadratic formula with the signed discriminant and the entire numerator divided by twice the leading coefficient.',
         'A:Give both exact roots in simplified Cartesian form.'),
        ('M:Complete the square in the stated shifted variable and retain the translation.',
         'A:Give both exact Cartesian roots.',
         'R:Verify both signed coefficient invariants, sum and product, against the expanded quadratic.'),
        ('M:Relate the imaginary-part magnitude to the unknown constant using a completed square or the conjugate-root invariants.',
         'A:Give the unique exact value of k.',
         'R:Give both roots and verify that the magnitude condition fixes k uniquely.'),
        ('M:Complete the square or obtain an equivalent two-branch root formula.',
         'A:Give the non-real interval, the conjugate root formula there and the exact common modulus.',
         'A:Give both repeated-root parameter values and their repeated roots.',
         'R:Use the positive product and signed sum (or exact inequalities) to classify the signs of both distinct real roots.',
         'R:Give the real-root branches and justify that the three parameter cases are disjoint and exhaustive.')),
    'conjugate-deduction': (
        ('A:Give the correct reflection, changing only the imaginary sign.',),
        ('A:Correctly evaluate or identify the unique root of the supplied non-real linear polynomial and reject the claim.',
         'R:State the real-coefficient hypothesis for the general theorem and explain why conjugating the evaluation gives another root.'),
        ('M:Apply the conjugate-root theorem under the real-coefficient hypothesis, without expanding or solving the polynomial.',
         'A:Give the complete set of three distinct roots, with no additional root.'),
        ('R:Establish that a real polynomial forces the conjugate with exactly the same multiplicity.',
         'A:Give the forced conjugate, its multiplicity and the minimum degree four.',
         'R:Justify the degree lower bound and its attainability using a real quartic with the stated repeated pair.'),
        ('M:Use the conjugate-root theorem to obtain the sum of the two non-real roots.',
         'M:Apply the signed monic cubic coefficient identity to determine the remaining root.',
         'A:Give all three roots and justify that the third value is real, uniquely fixed and compatible with the coefficient.'),
        ('M:Deduce the two forced distinct conjugate roots.',
         'A:Give the minimum degree and monic polynomial when the second root belongs to the original pair.',
         'A:Give the minimum degree and monic polynomial for the additional real root at h=0.',
         'A:Give the degree-four monic product for every remaining h, keeping the distinct conjugate pair.',
         'R:Prove both the forced-degree lower bounds and attainability, so every parameter case is covered.')),
    'conjugate-factor': (
        ('A:Give the correct real product of the conjugates.',),
        ('A:Give the corrected exact positive constant term.',
         'R:Explain that the imaginary square and the sign in the difference of squares give a positive contribution.'),
        ('M:Identify the forced conjugate and form the product of the two linear factors, or an equivalent real quadratic construction.',
         'A:Give the exact monic real quadratic factor.'),
        ('M:Parameterise the forced real quadratic as a nonzero scalar times the conjugate factor.',
         'M:Use the supplied value at the real coordinate to solve for that scalar.',
         'A:Give the exact polynomial including its nonmonic leading coefficient.'),
        ('M:Construct the real monic factor from the supplied root and its conjugate.',
         'M:Begin polynomial division by obtaining the leading quotient term and subtracting its product with the divisor.',
         'M:Continue division with the next quotient term and the corresponding subtraction.',
         'A:Finish the division, giving the correct quotient and zero remainder, and state both monic factors.',
         'R:Establish irreducibility over the reals for both factors by negative discriminants or equivalent exact reasoning.'),
        None),
    'solve-cubic': (
        ('M:Divide the cubic by the supplied linear factor to obtain the quadratic.',
         'A:Give the two other real roots.'),
        ('A:Give the real root of the linear factor.',
         'R:Use both imaginary square-root branches to give the conjugate pair and correct the claim that all three roots are real.'),
        ('M:Use the correct linear divisor and carry out the first quotient-term reduction.',
         'M:Carry out the next quotient-term reduction using the reduced dividend.',
         'M:Carry out the final quotient-term reduction.',
         'A:Obtain the complete correct quadratic quotient with zero remainder.',
         'M:Solve the resulting quadratic over the complex numbers using a valid two-branch method.',
         'A:Give all three exact roots, including the supplied root.'),
        ('M:Deduce the conjugate of the supplied non-real root.',
         'M:Construct the real quadratic factor from the conjugate pair.',
         'M:Carry out a valid division or coefficient-elimination method to determine the remaining linear factor without guessing.',
         'A:Obtain the exact remaining linear factor with zero remainder or verify its exact product with the quadratic.',
         'A:Give the complete root set.'),
        ('M:Substitute the supplied root and use the linear equation in the unknown constant to establish its unique value.',
         'M:Use the conjugate pair and exact division or equivalent factor construction to recover the linear factor.',
         'A:Give the correct constant and all three roots.'),
        ('M:Remove the known linear factor and obtain the parameter-dependent quadratic quotient.',
         'A:Give both remaining root branches together with the supplied root.',
         'R:Classify negative h and h=0, distinguishing a non-real simple pair and a double real root different from the known root.',
         'R:Test when the quotient also vanishes at the known root, give the exact collision value and multiplicities, and distinguish all other positive h.')),
    'solve-quartic': (
        ('M:Apply the zero-product rule to both factors.',
         'A:Give all four distinct real roots, including both signs.'),
        ('A:Give both exact real roots of the first factor.',
         'A:Give both exact imaginary roots of the second factor.',
         'R:Use the two quadratic branches and their disjoint root sets to reject the two-root claim.'),
        ('M:Use the supplied quadratic divisor to carry out the leading quotient-term reduction.',
         'M:Carry out the next quotient-term reduction using the reduced dividend.',
         'M:Carry out the final quotient-term reduction.',
         'A:Obtain the correct remaining quadratic quotient and zero remainder.',
         'A:Give all four exact roots from both quadratic factors.'),
        ('M:Deduce the conjugate root and construct the real monic quadratic factor.',
         'M:Carry out the initial polynomial-division reduction.',
         'M:Carry out the next division reduction using the reduced dividend.',
         'A:Obtain the exact remaining quadratic with zero remainder.',
         'M:Solve the remaining quadratic by factoring or another valid exact method.',
         'A:Give all four roots including the supplied conjugate pair.'),
        ('M:Substitute the given non-real root and recover the constant from the resulting linear equation.',
         'M:Use the conjugate factor and recover the second quadratic by valid division or equivalent factor construction.',
         'A:Give the correct constant and the complete set of four exact roots.'),
        ('M:Divide by the given irreducible factor to obtain the variable quadratic.',
         'A:Give the fixed conjugate pair and the two parameter-dependent root branches.',
         'R:Classify both exceptional parameters: the variable factor has a double real root at zero and coincides with the fixed factor at the negative squared imaginary magnitude.',
         'R:Prove there are no other repeated roots, classifying four simple roots as all non-real or two real and two non-real according to the sign of h.')),
    'verify-roots': (
        ('M:Substitute the specified real value into every term of the polynomial, retaining the signs.',
         'A:Obtain exact zero and conclude it is a root.'),
        ('M:Obtain the exact linear-times-quadratic factorisation or equivalent polynomial division.',
         'R:Show that the quadratic is nonzero at the real root, so it is simple, and correct the missing conjugate in the list.'),
        ('M:Multiply the conjugate linear factors to form the real quadratic, or multiply the three stated factors directly.',
         'A:Recover the exact original monic cubic.',
         'R:Use the three distinct degree-one factors to establish completeness and simplicity of every root.'),
        ('M:Verify the exact factorisation including the squared linear factor.',
         'R:Establish the two distinct non-real roots of the quadratic and show it does not vanish at the real root.',
         'A:Give the correct multiplicity of every proposed root.'),
        ('A:Obtain the exact constant from a valid substitution of the supplied root.',
         'M:Recover the full polynomial factorisation, with the repeated real factor.',
         'R:Reject the claimed complete list and justify all corrected multiplicities by checking distinctness and disjoint factors.'),
        ('M:Identify the common monic conjugate-pair factor for both proposed lists and every parameter pair.',
         'A:Give the exact coefficient pair required by list A, from the squared real linear factor.',
         'A:Give the exact coefficient pair required by list B, from the repeated conjugate quadratic factor.',
         'R:Establish both sufficiency and necessity by the full monic factorisations, prove the parameter pairs differ and explain why the common two roots alone give no parameter information.')),
}
TARGETS = {(p,t) for p, rows in DESIGNS.items() for t,row in enumerate(rows,1) if row is not None}


def base(path):
    return importlib.import_module('calibration_' + BANKS[path] + '_bank')


def revise(path,tier,v):
    if type(tier) is not int or type(v) is not int or (path,tier) not in TARGETS or v not in (1,2,3):
        raise ValueError('Not FM-16AX')
    p=base(path).make(path,tier,v)
    steps=p['worked_solution_latex']
    a,b,d=v+1,v+3,3*v+5
    if path=='complex-discriminant' and tier==2:
        steps[1]=f'First: (-{2*a}) squared - 4(1)({a*a}) = 0. Second: (-{2*a}) squared - 4(1)({a*a+b*b}) = {-4*b*b}. Hence the first has a repeated real root and the second two distinct non-real conjugate roots.'
    if path=='complex-quadratic' and tier==3:
        steps[1]=f'The quadratic formula gives x=(-{2*b} +/- sqrt(D))/{2*a}; since D is negative, use sqrt(D)=i sqrt(-D) and both signs. Simplifying gives {p["final_answer_latex"]}.'
    if path=='complex-quadratic' and tier==4:
        steps[-1]=f'The expanded monic quadratic has linear coefficient {2*(b-a)} and constant {a*a-2*a*b+d*d}. The computed roots have sum {2*(a-b)} and product {(a-b)**2+d*d-b*b}, agreeing with the negative of the linear coefficient and the constant, respectively.'
    if path=='conjugate-deduction' and tier==4:
        steps[0]='If P(x)=(x-z)^2 Q(x) with Q(z) nonzero, conjugating the coefficients gives P(x)=(x-conjugate(z))^2 Q*(x), where Q* is obtained by conjugating the coefficients of Q, because P has real coefficients. Evaluating Q* at conjugate(z) gives the nonzero conjugate of Q(z), proving that its multiplicity is exactly two.'
    if path=='verify-roots' and tier==1:
        # G=(x+d)(x^2-2ax+a^2+b^2), written out before substituting.
        B=d-2*a; C=a*a+b*b-2*a*d; D=d*(a*a+b*b)
        terms=[-d**3,B*d*d,C*(-d),D]
        steps[0]=f'At x=-{d}, the expanded cubic evaluates to (-{d}) cubed + ({B})(-{d}) squared + ({C})(-{d}) + {D} = ({terms[0]}) + ({terms[1]}) + ({terms[2]}) + ({terms[3]}) = 0.'
    old=p['rubric']; design=DESIGNS[path][tier-1]
    if len(design)!=len(old) or any(row['marks']!=1 or 'type' in row for row in old):
        raise ValueError('Unreviewed AX rubric structure')
    rub=[]
    for spec in design:
        kind, criterion=spec.split(':',1)
        if kind=='M':
            criterion+=' Accept equivalent valid methods respecting the question restrictions. Retain independently demonstrated method credit after an arithmetic slip.'
        elif kind=='A':
            criterion+=' Require the specified correct exact result; do not automatically award accuracy for an incorrect result.'
        else:
            criterion+=' Accept equivalent valid reasoning; require conclusions to follow from the stated constraints. Preserve demonstrated reasoning credit when it remains independently valid after an arithmetic slip.'
        rub.append({'type':kind,'marks':1,'criterion':criterion})
    p['rubric']=rub
    return p
