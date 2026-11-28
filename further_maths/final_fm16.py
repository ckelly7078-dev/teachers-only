"""Final FM-16 editorial successor, independent of release or teacher approval."""
import copy
import hashlib
import json
from pathlib import Path
from active_difficulty import require
from marking_review import fingerprint, validate_review
from marking_batch import read_batch
from successor_bq import SuccessorResolver, safe_parts, fields
from readiness_bo import conservative_preview_eligible
from scope_review_bl import WATCH

REVISION = 'FM-16FINAL'
TARGETS = tuple(f'CAL.invariant-lines.T5.V{v}' for v in (1, 2, 3))


def replacement(old):
    """Independent affine-line classification, no longer restricted to the origin."""
    p = old['payload']; v = p['variant']
    require(old['id'] in TARGETS and p['path'] == 'invariant-lines' and p['tier'] == 5
            and v in (1,2,3) and old['revision'] == 'FM-16BC' and old['marks'] == 3
            and old['teacher_approved'] is False, 'Unexpected predecessor')
    k,d = v+1,v+3
    # The predecessor's direction facts must correspond to this same matrix.
    require(p['facts'] == [{'matrix': [['1'], ['0']]}, {'matrix': [[str(k)], [str(d-1)]]}], 'Wrong predecessor directions')
    from fractions import Fraction
    m=Fraction(d-1,k)
    slope=rf'\frac{{{m.numerator}}}{{{m.denominator}}}'
    q=copy.deepcopy(old); p=q['payload']
    q.update(revision=REVISION,marks=5)
    p.update(question_latex=rf'Under $C=\begin{{pmatrix}}1&{k}\\0&{d}\end{{pmatrix}}$, classify all affine lines mapped onto themselves, including vertical lines. Identify which are fixed pointwise and prove completeness.',
             final_answer_latex=rf'The invariant lines are $y=0$ and $y={slope}x+c$ for every real $c$. Only $y=0$ is fixed pointwise. No vertical lines are invariant.',
             worked_solution_latex=[rf'Use $X=x+{k}y$ and $Y={d}y$. For $y=mx+c$, require $Y=mX+c$ for all $x$.',
               rf'Coefficient comparison gives $m({d}-1-{k}m)=0$ and $({d}-1-{k}m)c=0$.',
               rf'When $m=0$, $c=0$. When $m={slope}$, $c$ is arbitrary. On a vertical line $x=x_0$, the image $X=x_0+{k}y$ varies with $y$, so no vertical line is invariant.',
               rf'Fixed points satisfy $(C-I)\begin{{pmatrix}}x\\y\end{{pmatrix}}=0$, hence $y=0$. As $\det C={d}$ is nonzero, inclusion of each invariant line is equality; the two slope branches and vertical case exhaust all affine lines.'],
             facts={'matrix':[[1,k],[0,d]],'nonvertical_families':[{'slope':'0','intercept':'0'},{'slope':str(m),'intercept':'arbitrary_real'}], 'vertical_invariant':False,'pointwise_fixed':'y=0','determinant':d},
             rubric=[{'type':t,'marks':1,'criterion':c} for t,c in [
                 ('M','Map a general nonvertical affine line and impose setwise invariance; accept equivalent normal or eigenvector method.'),
                 ('M','Derive both slope and intercept constraints.'),
                 ('A','Give both correct families, including arbitrary intercept for the nonhorizontal family.'),
                 ('R','Exclude vertical lines and justify exhaustiveness using invertibility or equivalent argument.'),
                 ('R','Identify exactly the pointwise-fixed line by solving the fixed-point condition.')]],
             demand_rationale='Classify all affine invariant lines for a coupled nonsingular map, including the arbitrary-intercept branch, then distinguish pointwise fixation and prove exhaustion.',
             progressive_hints=['Write a general affine line and impose equality of the original and image equations.','Compare both coefficients and analyse vertical lines separately.'],
             likely_mistake='Restricting the classification to lines through the origin or confusing setwise invariance with pointwise fixation.')
    check(q)
    return q


def check(item):
    """Exact independent normal-vector and fixed-point oracle for new facts."""
    import sympy as s
    f=item['payload']['facts']; C=s.Matrix(f['matrix']); m=s.Rational(f['nonvertical_families'][1]['slope'])
    require(C.shape==(2,2) and C.det()==f['determinant'] and C.det()!=0, 'Determinant mismatch')
    normals=C.T.eigenvects()
    actual={(e,tuple(n/n[1])) for e,_,ns in normals for n in ns if n[1]!=0}
    require(len(actual)==2 and actual=={(C[1,1],(0,1)),(1,(-m,1))}, 'Incorrect invariant normals')
    require(all(n[1]!=0 for _,_,ns in normals for n in ns) and f['vertical_invariant'] is False,'Vertical line mismatch')
    require(f['nonvertical_families']==[{'slope':'0','intercept':'0'},{'slope':str(m),'intercept':'arbitrary_real'}], 'Intercept mismatch')
    require((C-s.eye(2)).nullspace()==[s.Matrix([1,0])] and f['pointwise_fixed']=='y=0','Fixed set mismatch')
    require(item['marks']==5==sum(r['marks'] for r in item['payload']['rubric']), 'Mark mismatch')
    for text in fields(item['payload']).values(): safe_parts(text)
    return True


class FinalResolver(SuccessorResolver):
    def _resolve(self,path,tier,variant):
        old=super()._resolve(path,tier,variant)
        return replacement(old) if old['id'] in TARGETS else old


def load_final_bank(root):
    """Explicit opt-in; never silently replace the prior BQ runtime."""
    from knowledge_fm17 import KnowledgeBank
    root=Path(root)
    manifest=json.loads((root/'FM16FINAL-runtime-manifest.json').read_text())
    required={'as1.sqlite','FM16BQ-successor-edits.jsonl','FM16FINAL-current-review-ledger.jsonl','FM16FINAL-scope-dispositions.jsonl'}
    require(manifest['checkpoint']==REVISION and required <= set(manifest['sha256']), 'Invalid final manifest')
    for name in required:
        with (root/name).open('rb') as stream:
            require(hashlib.file_digest(stream,'sha256').hexdigest()==manifest['sha256'][name],'Private snapshot mismatch')
    edits=read_batch(root/'FM16BQ-successor-edits.jsonl'); reviews=read_batch(root/'FM16FINAL-current-review-ledger.jsonl')
    bank=KnowledgeBank(root/'as1.sqlite',edits,reviews,resolver=FinalResolver(edits))
    rows=read_batch(root/'FM16FINAL-scope-dispositions.jsonl')
    expected={f'CAL.{p}.T{t}.V{v}' for p,t in WATCH for v in (1,2,3)}
    require(len(rows)==len(expected) and {r['id'] for r in rows}==expected, 'Incomplete scope dispositions')
    for row in rows:
        item=bank.items[row['id']]; p=item['payload']
        require(row['fingerprint']==fingerprint(item) and row['selection']=='learning_only'
                and row['teacher_approved'] is False and row['exam_ready'] is False
                and not conservative_preview_eligible(bank.resolver,p['path'],p['tier'],'exam_candidate_preview'), 'Invalid scope disposition')
    return bank
