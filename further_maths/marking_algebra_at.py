"""FM-16AT: evidence for all 39 remaining algebra T3 items; no active changes."""
import json

# Frozen version fingerprints and individually checked calculations.
ROWS = {
    'combined-roots': [
        ('7fc53a00a91577519cb95b520f1a79b00fdaf393bc8e30333fbf3a87c72b2c43', '9-8=1; 14-4*9+16=-6; reciprocal sum -1/6, product -1/6; x^2+x/6-1/6=0'),
        ('719f28ac8239af9bcf19ae7dd5613c2e6bb36791035e641de56adb99d18c2d51', '12-10=2; 27-5*12+25=-8; reciprocal sum -1/4, product -1/8; x^2+x/4-1/8=0'),
        ('137d61083d0cb32f188409d6885e931b4a6762e5c3b74f3e8f22ffe19ac84b96', '15-12=3; 44-6*15+36=-10; reciprocal sum -3/10, product -1/10; x^2+3*x/10-1/10=0')],
    'cube-sums': [
        ('9aaecf6529c80996a2057978aa1d99a86a66aee7e746ecceaa6f6db3c3d85f85', '9^3-3*14*9=351'),
        ('ab6c4f12fbc3a92cca6821f190b2cc74fd195b6872503daf938e7ea5c4c0b65a', '12^3-3*27*12=756'),
        ('a66450495fd787878a1e8f033a6b821db232645068ba1872e49239f146e33bd5', '15^3-3*44*15=1395')],
    'factor-connection': [
        ('dd3c256bdf1870edf769dfde3df758150a385d0bbd63ab02622749ca3322bbb9', '2*7=14; 2-4*7=-26; -4; 14*x^2-26*x-4'),
        ('aeb76e1b05cb125e21b3a62fbc6525e457d15286d7616bd7a8ce6e9f5a77479c', '3*9=27; 3-5*9=-42; -5; 27*x^2-42*x-5'),
        ('724d10a1560f638502f92b4aefb9ae952cda65eecf49945437de674dbae2b78e', '4*11=44; 4-6*11=-62; -6; 44*x^2-62*x-6')],
    'quadratic-from-roots': [
        ('b5290c6fd099207b04dc4e77809ab2d47510a93921cb1e3d525f531fc3d60e48', 'S=7, P=-8; x^2-7*x-8=0'),
        ('e4254ec58d75c5c75d96ecd3962ca664222ed13bbe9000810d2d2df47862a0c8', 'S=9, P=-15; x^2-9*x-15=0'),
        ('d6523eb9adb59a498ce0ead756333e3d29a9300a68f0e394417bca3b81c1a0e0', 'S=11, P=-24; x^2-11*x-24=0')],
    'reciprocal': [
        ('03811bce65e42c4905a775fb5b8828ea6609a0f68968fdb742a2b18b4e79e872', '6/8=3/4; 1/8; x^2-3*x/4+1/8=0'),
        ('271d650c7c1465ce9dc1a90ba7624174647f9b5755a5eaf6421358fa2f395b07', '8/15; 1/15; x^2-8*x/15+1/15=0'),
        ('be0bd41b2b7390b13c8512f5986c3ac2cb0eccd6c5fa33869d7b8d3d85805bf0', '10/24=5/12; 1/24; x^2-5*x/12+1/24=0')],
    'reciprocal-sums': [
        ('78ce03cffca68c4d075e200de4402b94d4f573979b8b1ec1adf3bc8ed98139db', '9/14; P=14 nonzero'),
        ('51e69e816234cff8764b47519527bf88c87b63d719df15dba3a6a76505201e5e', '12/27=4/9; P=27 nonzero'),
        ('17a440fc61c31bfd40884b68ef9302d1d71c25840de155e3f0f57ec60e08a5a9', '15/44; P=44 nonzero')],
    'root-ratios': [
        ('484b058a0d7e218bccf09830493c6d7a0b8a52f90827be742139d0e40f25c90a', '(8^2-2*12)/12=10/3; product 1; x^2-10*x/3+1=0'),
        ('c4e7d2f798a1cf5e5341626c0b942d7c7c5c80e7f25bf4a41232fa1fa05b79f8', '(11^2-2*24)/24=73/24; product 1; x^2-73*x/24+1=0'),
        ('2d001118934867aa09faff7eb5feec54b359054e207027033acd8c88ea001e79', '(14^2-2*40)/40=29/10; product 1; x^2-29*x/10+1=0')],
    'root-squares': [
        ('aa3b326cc93e6f024ad5d15190e7bd6ccc4e59a0ae024e4bccce0f311d4d61d3', '12/2=6; 16/2=8; 6^2-2*8=20'),
        ('78c3923440079ca76218f32ca9b903e2c025db9216dbbaa351fb3c8617368c33', '16/2=8; 30/2=15; 8^2-2*15=34'),
        ('1f809dd663d1ce61b4a3a79c23e17b7f7e2c0aaca2ee6ad537c3276ebdfbe846', '20/2=10; 48/2=24; 10^2-2*24=52')],
    'scaled-roots': [
        ('fc8cc7f635398c48f0bd78c06034a9ea320310c789946074a628f0adc667cd31', '-7*8=-56; 49*12=588; x^2+56*x+588=0'),
        ('8e9f6266c438c5d8d91000ef7954ad9998956a5f01a6dcb01c3f370633576cb0', '-9*11=-99; 81*24=1944; x^2+99*x+1944=0'),
        ('401e99cca732892ff1992a771c2f64cab8eef4087ac92795aacf26de7b70c742', '-11*14=-154; 121*40=4840; x^2+154*x+4840=0')],
    'shifted-products': [
        ('79e6e05f785b5d17394b760274039a57791952b408d1bc1506f66588a49b2a86', '14-4*9+16=-6'),
        ('4795c41f2468341b2a1535b6cfdc919870351fee34151f129bc81d2790bd65f3', '27-5*12+25=-8'),
        ('418950032cd6ca51aab2f715c1eb99458372c8946177df06bf3213f70c4a7b0b', '44-6*15+36=-10')],
    'shifted-roots': [
        ('d1ae26466f63051bf81459ba6d1737d5df55ad12100dd5808564b2a8cda63fd5', '8-14=-6; 12-7*8+49=5; x^2+6*x+5=0'),
        ('bf433757f677c5ba3eba69acad8413ea5eb7de944d9fb9b2f5fac35b0eb0a063', '11-18=-7; 24-9*11+81=6; x^2+7*x+6=0'),
        ('78638ac1361f288f492863edff461c66d06f2d761008c0443f326cfd52c230d7', '14-22=-8; 40-11*14+121=7; x^2+8*x+7=0')],
    'squared-roots': [
        ('c1db6cf34742306d8bd24d98cdf1a21de299b3dc1b4e0c1e97c33c371cef9035', '8^2-2*12=40; 12^2=144; x^2-40*x+144=0'),
        ('4b1426e09480fb97c925754e134381ac207b0c43e4cf27bcbf048acf627a9f09', '11^2-2*24=73; 24^2=576; x^2-73*x+576=0'),
        ('0db8573e45cd320c2ce698ecf05e06234e6fd1f955bbec894177e20657a185cf', '14^2-2*40=116; 40^2=1600; x^2-116*x+1600=0')],
    'symmetric-parameter': [
        ('cbe8bc7800ddd2ddd819610eb2ec739498f75d06a469827e44b58b1c22ac40d4', '53+28=81; k=+/-9; discriminant 81-56=25'),
        ('46702593a6603f85830444898c3233eb59d7baee11311e73753195874937bd99', '90+54=144; k=+/-12; discriminant 144-108=36'),
        ('ab6e61df74a323099f5fe1a95f60b4b563c423f20a0fc5aff02a03c6e578b182', '137+88=225; k=+/-15; discriminant 225-176=49')],
}

# Types, proposed criterion evidence, alternate method, boundary evidence,
# presentation finding, allocation finding (empty string means no requested change).
NOTES = {
    'combined-roots': ('MMA', ['Obtain shifted sum S-2d and product P-dS+d^2.', 'Form both reciprocal invariants using the shifted product.', 'Construct the exact monic equation.'], 'Substitute x=d+1/y into the original polynomial and normalise.', 'Each shifted product is negative and nonzero as the arithmetic shows; both reciprocals exist.', '', ''),
    'cube-sums': ('MMA', ['Obtain signed root sum and product from coefficients.', 'Apply S^3-3PS.', 'Evaluate the exact cube sum.'], 'Factor alpha^3+beta^3 as (alpha+beta)((alpha+beta)^2-3alpha*beta).', '', '', ''),
    'factor-connection': ('AAA', ['Correct leading coefficient.', 'Correct signed mixed coefficient from both cross terms.', 'Correct constant coefficient.'], 'Accept a grid, distributive expansion or direct coefficient products.', '', 'Replace the irrelevant monic-root-formula warning with omission of a cross term or incorrect sign.', ''),
    'quadratic-from-roots': ('MA', ['Use x^2-Sx+P or equivalent symbolic coefficient construction.', 'State the complete exact monic equation.'], 'Expand the formal product (x-alpha)(x-beta) using the supplied invariants.', '', '', ''),
    'reciprocal': ('MA', ['Apply S/P and 1/P, or reciprocal polynomial substitution with normalisation.', 'Give the exact monic equation.'], 'Reverse coefficients by substituting x=1/y and multiplying by y^2, then normalise.', 'All original products in the calculations are nonzero, so neither original root is zero.', 'Explicitly state nonzero product and show both reciprocal identities in the solution.', 'The current first criterion rewards original invariants only; require the reciprocal transformation method for M1 and reserve A1 for the final equation.'),
    'reciprocal-sums': ('MMA', ['Obtain root sum and product by coefficient comparison.', 'Combine the reciprocals over the common denominator P.', 'Evaluate the exact fraction.'], 'Use the sum of roots of the reversed polynomial.', 'The product in every calculation is nonzero; the common denominator is valid.', '', ''),
    'root-ratios': ('MMA', ['Form (S^2-2P)/P for the ratio sum.', 'Cancel factors to establish product one, noting P nonzero.', 'Construct the exact monic equation.'], 'Use alpha/beta+beta/alpha = S^2/P-2 and the reciprocal-pair product.', 'Each P is positive and nonzero; both ratios are defined.', '', ''),
    'root-squares': ('MA', ['Use signed coefficient ratios and the identity S^2-2P.', 'Give the exact square sum.'], 'Normalise first, or use the quadratic recurrence for the sum of squares.', '', 'Remove the unrelated warning about discarding a negative root-sum branch; retain the cross-term warning.', 'With two marks, require the square-sum identity in the method criterion, not just coefficient comparison.'),
    'scaled-roots': ('MMA', ['Obtain original sum and product.', 'Transform with signed scale c for S and c^2 for P.', 'Construct the exact monic equation.'], 'Substitute x=y/c in the original equation and normalise.', 'Each scale is negative and nonzero; the product scale is positive.', '', ''),
    'shifted-products': ('MMA', ['Obtain original root sum and product.', 'Expand to P-dS+d^2.', 'Evaluate the exact signed product.'], 'Evaluate the monic original polynomial at d.', '', '', ''),
    'shifted-roots': ('MA', ['Apply S-2d and P-dS+d^2, or an equivalent shifted polynomial substitution.', 'Construct the exact monic equation.'], 'Substitute x=y+d into the original polynomial and expand.', '', 'Show how both new invariants are obtained instead of only stating their numerical values.', 'The first criterion needs an explicit transformation method, not just two computed coefficients.'),
    'squared-roots': ('MMA', ['Obtain original S and P.', 'Use S^2-2P and P^2 for the transformed invariants.', 'Construct the exact monic equation.'], 'Eliminate the sign of x from the original equation using y=x^2; rearrange to a monic equation in y.', '', '', ''),
    'symmetric-parameter': ('MAR', ['Apply S^2-2P to derive the equation for k.', 'Obtain both signs of k.', 'Check the discriminant for both candidates and conclude completeness.'], 'Use the identity (alpha+beta)^2=alpha^2+beta^2+2alpha*beta, then check reality.', 'Both signs have the same strictly positive discriminant, as the arithmetic verifies; no other roots of k^2 are possible.', '', ''),
}


def records():
    for path, rows in ROWS.items():
        types, criteria, alternate, boundary, presentation, amendment = NOTES[path]
        for v, (fp, calculation) in enumerate(rows, 1):
            allocation = [{'criterion_index': i, 'marks': {t: int(t == typ) for t in ('M', 'A', 'R')}, 'evidence': criterion} for i, (typ, criterion) in enumerate(zip(types, criteria))]
            follow = ('Assess each coefficient independently; do not award an incorrect coefficient.' if path == 'factor-connection' else 'Retain demonstrated method credit after arithmetic slips; no automatic final accuracy credit for an incorrect result. Judge subsequent valid reasoning on its own merits.')
            checks = {
                'mathematical_correctness': {'decision': 'pass', 'evidence': calculation + '; agrees with the inspected answer and worked calculations.'},
                'criterion_allocation': {'decision': 'revise' if amendment else 'pass', 'evidence': amendment or 'Proposed allocation: ' + ' '.join(criteria)},
                'alternative_methods': {'decision': 'pass', 'evidence': alternate + ' Respect the instruction not to solve the original roots where present.'},
                'consequential_errors': {'decision': 'pass', 'evidence': follow},
                'boundary_cases': {'decision': 'pass' if boundary else 'not_applicable', 'evidence': boundary or 'Fixed numerical coefficients; no variable-domain or denominator exception in this task.'},
                'presentation': {'decision': 'revise' if presentation else 'pass', 'evidence': (presentation or 'Prompt, final answer, hints and worked calculations are consistent.') + ' Text inspected, not rendered.'},
            }
            yield {'id': f'CAL.{path}.T3.V{v}', 'fingerprint': fp, 'reviewer': 'AI editorial algebra review FM-16AT (teacher approval pending)', 'teacher_approved': False, 'checks': checks, 'allocation': allocation}


if __name__ == '__main__':
    for record in records():
        print(json.dumps(record, sort_keys=True))
