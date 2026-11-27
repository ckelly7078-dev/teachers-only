"""Preservation and independent foundational vector boundary checks."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_bf import BANKS,TARGETS,base,revise
from marking_design_bf import records
from marking_review import inventory_entry
from marking_batch import validate_batch

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver()

    def test_all_variants(self):
        self.assertEqual(len(TARGETS),56)
        retained={('scalar-product',3):'FM-16AS',('scalar-product',6):'FM-16AO',('perpendicular-parameter',6):'FM-16AO',('cross-product',6):'FM-16AK'}
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
                        else:self.assertEqual(item['revision'],retained[p,t])
                        for text in [x['question_latex'],x['final_answer_latex'],*x['worked_solution_latex']]:
                            self.assertEqual(text.count('$')%2,0)
                            self.assertEqual(text.count('\\begin{'),text.count('\\end{'))

    def test_ledger(self):
        rows=list(records(self.r));self.assertEqual(len(rows),180)
        self.assertEqual(validate_batch(rows,self.r)['statuses'],{'editorial_review_recorded':180})

    def test_invalid_target(self):
        for key in [('scalar-product',3,1),('cross-product',6,1),('perpendicular-parameter',6,1),('unit-vector',True,1),('cross-linearity',2,True)]:
            with self.assertRaises(ValueError):revise(*key)

    def facts(self,p,v):return self.r._resolve(p,6,v)['payload']['facts']

    def test_distance_circle_intersections(self):
        r,h=s.symbols('r h');x,y=s.symbols('x y')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('vector-components',v)
            x0,R=map(s.sympify,f[:2]);self.assertEqual(s.expand((x0+a)**2-(x0-a)**2),h*h-r*r)
            self.assertEqual(s.simplify((x0-a)**2+R+b*b-r*r),0)
            for yy in (0,2):
                rr=s.sqrt(a*a+b*b+yy*yy); rad=s.simplify(R.subs({r:rr,h:rr}));self.assertEqual(rad,yy*yy)
            self.assertLess(R.subs({r:0,h:0}),0)

    def test_convex_triangle(self):
        h,k=s.symbols('h k')
        for v in (1,2,3):
            a,b=v+1,v+3;A,B,z,C=map(s.sympify,self.facts('vector-combinations',v));U=s.Matrix([a,0,1]);V=s.Matrix([0,b,1]);self.assertEqual(s.Matrix.hstack(U,V).rank(),2)
            self.assertEqual(A*U+B*V,s.Matrix([h,k,z]));self.assertEqual(s.simplify(A+B+C),1)
            for x,y,inside,boundary in [(0,0,True,True),(a,0,True,True),(0,b,True,True),(a/2,b/2,True,True),(s.Rational(a,4),s.Rational(b,4),True,False),(-1,0,False,False),(a,b,False,False)]:
                vals=[q.subs({h:s.sympify(x),k:s.sympify(y)}) for q in (A,B,C)];self.assertEqual(all(q>=0 for q in vals),inside)
                if inside:self.assertEqual(any(q==0 for q in vals),boundary)

    def test_unit_sphere_boundary(self):
        h,k=s.symbols('h k')
        for v in (1,2,3):
            a=v+1;R=s.sympify(self.facts('unit-vector',v)[0]);self.assertEqual(s.simplify(h*h+(k/a)**2+R),1)
            for x,y,count in [(0,0,2),(1,0,1),(0,a,1),(1,a,0),(2,0,0)]:
                q=R.subs({h:x,k:y});roots=[] if q<0 else {s.sqrt(q),-s.sqrt(q)};self.assertEqual(len(roots),count)
                for z in roots:
                    w=s.Matrix([x,s.Rational(y,a),z]);self.assertEqual(w.dot(w),1)

    def test_perpendicular_exclusions(self):
        h,k=s.symbols('h k')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('perpendicular-test',v);expr,forbidden=map(s.sympify,f[:2]);dot=s.Matrix([h,k,0]).dot(s.Matrix([k-a,h-b,0]));self.assertEqual(s.simplify(dot.subs(k,expr)),0)
            self.assertNotEqual(s.simplify(dot.subs(h,forbidden)),0)
            for x in (0,b,-1,b+1):
                y=expr.subs(h,x);u=s.Matrix([x,y,0]);w=s.Matrix([y-a,x-b,0]);self.assertEqual(u.dot(w),0);self.assertEqual(u==s.zeros(3,1) or w==s.zeros(3,1),x in (0,b))

    def test_cross_order_length_threshold(self):
        c=s.Symbol('c')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('cross-order',v);U=s.Matrix([a,b,0]);V=s.Matrix([1,0,0]);self.assertEqual(s.sympify(f[2]),b)
            for C in (b,b+1):
                roots={tuple(s.Matrix(m['matrix']).applyfunc(s.sympify).subs(c,C)) for m in f[:2]};self.assertEqual(len(roots),1 if C==b else 2)
                for W in map(s.Matrix,roots):self.assertEqual(V.cross(W),U.cross(V));self.assertEqual(W.dot(W),C*C)

    def test_cross_linearity_equal_lengths(self):
        t,k,h=s.symbols('t k h')
        for v in (1,2,3):
            a=v+1;f=self.facts('cross-linearity',v);X,Y=[s.Matrix(m['matrix']).applyfunc(s.sympify) for m in f[:2]]
            self.assertEqual(X+Y,s.Matrix([a,0,0]));self.assertEqual(X.cross(Y).applyfunc(s.simplify),s.Matrix([0,k,h]));self.assertEqual(s.solve(X.dot(X)-Y.dot(Y),t),[s.sympify(f[2])]);self.assertFalse(f[3])

    def test_zero_cross_locus(self):
        h,k=s.symbols('h k')
        for v in (1,2,3):
            a=v+1;f=self.facts('zero-cross',v);U=s.Matrix([k,a,0]);V=s.Matrix([h,k,0]);self.assertEqual(U.cross(V)[2],s.sympify(f[0]));self.assertEqual(V.subs(h,s.sympify(f[1])),U*k/a)
            self.assertEqual(V.subs({h:0,k:0}),s.zeros(3,1));self.assertNotEqual(U.subs(k,0),s.zeros(3,1))

if __name__=='__main__':unittest.main()
