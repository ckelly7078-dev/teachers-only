"""FM-16AR: twelve manually inspected original questions, with frozen fingerprints."""
import json

REVIEWER = 'AI editorial pilot FM-16AR (teacher approval pending)'
# Each row binds a specific inspected item to its independently checked arithmetic.
ROWS = {
    'root-sum-product': [
        ('8a1bdb85e17f274aca0f0a5a1b24be6d7ec6fb835113d9d723fb0b85af570019','2x^2-7x+4: sum 7/2, product 2'),
        ('537e226f16bbfa6e7b8821d586c0f10d8cb5dc7cf7d9629939da33cbb435b72c','3x^2-9x+5: sum 3, product 5/3'),
        ('75ab0e38627b3fc33fbad839bddf553d1c3fa69f7eec34a3a35181befdc7f23e','4x^2-11x+6: sum 11/4, product 3/2'),
    ],
    'cartesian-product': [
        ('88b3dc1d2708055306e1c9b852f30f3eb5fa2165e2127d0948f39214901b30e6','16+8=24; -4+32=28; 24+28i'),
        ('0f79c79f5a23512832ef160168c317eff615fd72b09e919308a9208992e4b4e5','33+15=48; -9+55=46; 48+46i'),
        ('d282af9a184389349c20229812943551416061865bf817b9aa52f04f900ef7c9','56+24=80; -16+84=68; 80+68i'),
    ],
    'det-two': [
        ('3562cc62088d364cca5af3640ac00f00fb11d1de6ebee0186bdcca40d6ed53f2','2*3-(-2*3)=12'),
        ('806794e02386b7bb0a7fad5493ea2f44959f7cac594a6c6df2a06773c8888a7c','3*4-(-2*3)=18'),
        ('8c1af2b2decf6930ba691a97152469487cb6bf2352500b6689bcf6d1845bc40a','4*5-(-2*3)=26'),
    ],
    'scalar-product': [
        ('08bf01d47ccff1a21bcb50e064225acfa1d547ad59daae97fd1cf90f347a5c79','4-3+12=13'),
        ('2c8d29c785d25a85f63ad291db8d2ee4e4f325eb928e7a60efe8adf58432a1bf','6-4+15=17'),
        ('8715835ad9dd037654ddae534b93b787ff848e3779e4a77f358aa36e6a7bda65','8-5+18=21'),
    ],
}
# Allocation proposals are editorial guidance, not active mark scheme changes.
NOTES = {
    'root-sum-product': (
        'revise','Coefficient identification alone is insufficient for a method mark; move use of both signed Vieta ratios into the first criterion, reserve the second for both correct results.',
        'Accept normalising to a monic quadratic or matching coefficients of the factored polynomial; neither requires solving for roots.',
        'Proposed M1 for both correct ratio methods; A1 for both exact answers, no accuracy follow-through on an incorrect ratio.',
        'The leading coefficient is nonzero and the task does not require real roots; no parameter boundary is present.',
        'pass','The prompt explicitly excludes solving and the solution uses the two identities. Text and LaTeX delimiters inspected; no renderer used.',
        'Proposed M1 requires applying both identities, not merely identifying coefficients.','Proposed A1 requires both exact values.'),
    'cartesian-product': (
        'pass','Expansion is a substantive method and collection using i squared = -1 is accuracy; both marks are proportionate.',
        'Accept the component formula (ac-bd)+(ad+bc)i as equivalent to four-term expansion.',
        'M1 for complete signed expansion or equivalent; A1 for both correct components; a single arithmetic slip can retain method credit but not final accuracy.',
        'The two fixed factors involve nonzero components; no singular or variable-domain case occurs.',
        'pass','The Cartesian form, four terms and i squared reduction agree; the hint and misconception are relevant. Text and delimiters inspected, not rendered.',
        'M1 complete signed expansion or equivalent component formula.','A1 correct exact Cartesian result.'),
    'det-two': (
        'pass','The diagonal products establish method and signed subtraction establishes accuracy.',
        'Accept direct ad-bc evaluation or a valid cofactor expansion.',
        'M1 for signed diagonal products in determinant order or equivalent; A1 for exact determinant, not absolute value. A calculation slip may retain method credit.',
        'The specified 2x2 matrix is fixed and no parameter or singular classification is asked.',
        'revise','The misconception note also mentions losing a root of a squared parameter equation, unrelated to this task. Retain signed subtraction guidance only. Text inspected, not rendered.',
        'M1 correct signed determinant method.','A1 correct signed determinant.'),
    'scalar-product': (
        'pass','Matching components establishes method; adding all signed products to a scalar establishes accuracy.',
        'Accept a single correctly written component sum, or equivalent matrix multiplication of a row by a column.',
        'M1 for the complete corresponding-component method; A1 for the correct signed scalar, not a vector. Arithmetic slip may retain method credit.',
        'Both vectors are fixed and no angle or normalisation is required; no exceptional case occurs.',
        'pass','The component products, scalar sum, hint and misconception are consistent. Text and delimiters inspected, not rendered.',
        'M1 multiply all corresponding components.','A1 sum to the exact signed scalar.'),
}


def records():
    for path, rows in ROWS.items():
        decision, allocation, alternative, follow, boundary, presentation_decision, presentation, method, accuracy = NOTES[path]
        for variant, (fingerprint, calculation) in enumerate(rows,1):
            checks = {
                'mathematical_correctness': {'decision':'pass','evidence':calculation+'; agrees with the stored prompt, worked steps and final answer.'},
                'criterion_allocation': {'decision':decision,'evidence':allocation},
                'alternative_methods': {'decision':'pass','evidence':alternative},
                'consequential_errors': {'decision':'pass','evidence':follow},
                'boundary_cases': {'decision':'not_applicable','evidence':boundary},
                'presentation': {'decision':presentation_decision,'evidence':presentation},
            }
            yield {'id':f'CAL.{path}.T3.V{variant}','fingerprint':fingerprint,'reviewer':REVIEWER,'teacher_approved':False,'checks':checks,'allocation':[{'criterion_index':0,'marks':{'M':1,'A':0,'R':0},'evidence':method},{'criterion_index':1,'marks':{'M':0,'A':1,'R':0},'evidence':accuracy}]}


if __name__ == '__main__':
    for record in records():
        print(json.dumps(record,sort_keys=True))
