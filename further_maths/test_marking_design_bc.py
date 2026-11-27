"""Check marking preservation and independent transformation boundary examples."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_bc import BANKS,TARGETS,base,revise
from marking_design_bc import records
from marking_review import inventory_entry
from marking_batch import validate_batch

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver(historical_through='bh')

    def test_all_variants(self):
        self.assertEqual(len(TARGETS),46)
        for p in BANKS:
            for t in range(1,7):
                for v in (1,2,3):
                    with self.subTest(p=p,t=t,v=v):
                        item=self.r._resolve(p,t,v);x=item['payload']
                        self.assertEqual(inventory_entry(item)['status'],'typed_provisional')
                        self.assertFalse(item['teacher_approved'])
                        if (p,t) in TARGETS:
                            old=base(p).make(p,t,v)
                            self.assertEqual({k for k in old if old[k]!=x[k]},{'rubric'})
                            self.assertEqual(item['marks'],sum(z['marks'] for z in old['rubric']))
                        else:self.assertEqual(item['revision'],'FM-16AE' if p=='composition-order' else 'FM-16AI')
                        for text in [x['question_latex'],x['final_answer_latex'],*x['worked_solution_latex']]:
                            self.assertEqual(text.count('$')%2,0)
                            self.assertEqual(text.count('\\begin{'),text.count('\\end{'))

    def test_ledger(self):
        rows=list(records(self.r));self.assertEqual(len(rows),144)
        self.assertEqual(validate_batch(rows,self.r)['statuses'],{'editorial_review_recorded':144})

    def test_invalid_target(self):
        for key in [('invariant-lines',6,1),('composition-order',6,1),('figure-images',True,1),('basis-images',2,True)]:
            with self.assertRaises(ValueError):revise(*key)

    def test_affine_image_branches(self):
        t=s.symbols('t',real=True)
        for a in (2,3,4):
            b=a+2;k=-s.Rational(1,a)
            for h in (0,2,-3):
                M=s.Matrix([[1,a],[0,h]]);out=M*s.Matrix([t,k*t+b])
                self.assertEqual(s.simplify(out[0]),a*b)
                self.assertEqual(s.diff(out[1],t),h*k)
                self.assertEqual(s.diff(out,t)==s.zeros(2,1),h==0)
            for h in (0,2):
                M=s.Matrix([[1,a],[0,h]]);out=M*s.Matrix([t,2*t+b])
                self.assertNotEqual(s.diff(out[0],t),0)

    def test_fixed_space_and_singular_affine_lines(self):
        for a in (2,3,4):
            for k,h in [(1,1),(1,0),(3,1),(3,0)]:
                M=s.Matrix([[k,a],[0,h]])-s.eye(2)
                self.assertEqual(len(M.nullspace()),int(k==1 or h==1))
                if h==1 and k!=1:self.assertEqual(M*s.Matrix([-a,k-1]),s.zeros(2,1))
            for k in (0,1,2,-1):
                M=s.diag(1,k)
                self.assertEqual(M*s.Matrix([1,0]),s.Matrix([1,0]))
                self.assertEqual(M*s.Matrix([0,1])==s.zeros(2,1),k==0)

    def test_reflection_axis_exception(self):
        for p,h in [(0,0),(-3,0),(3,0),(3,4),(-3,4),(0,-2)]:
            M=s.Matrix([[p,h],[h,-p]]);rho=s.sqrt(p*p+h*h)
            self.assertEqual(M.T*M,rho**2*s.eye(2))
            if rho==0:self.assertEqual(M,s.zeros(2));continue
            d=s.Matrix([rho+p,h]);d=s.Matrix([h,rho-p]) if d==s.zeros(2,1) else d
            self.assertNotEqual(d,s.zeros(2,1));self.assertEqual(M*d,rho*d)
            n=s.Matrix([-d[1],d[0]]);self.assertEqual(M*n,-rho*n)

    def test_shear_composition_and_basis_degeneracy(self):
        q,r=s.symbols('q r',real=True)
        A=s.Matrix([[1,q],[0,1]]);B=s.Matrix([[1,0],[r,1]])
        self.assertEqual(B*A-A*B,s.diag(-q*r,q*r))
        for k,h in [(0,0),(0,2),(2,3),(-1,4)]:
            if k:
                M=s.Matrix([[2,s.Rational(h,k)],[1,3]])
                self.assertEqual(M*s.Matrix([2,k]),s.Matrix([4+h,2+3*k]))
            else:self.assertEqual(s.Matrix([4,2])==s.Matrix([4+h,2]),h==0)

if __name__=='__main__':unittest.main()
