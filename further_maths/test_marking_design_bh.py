"""Preservation and independent boundary checks for final vector pathways."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_bh import BANKS,TARGETS,base,revise
from marking_design_bh import records
from marking_review import inventory_entry
from marking_batch import validate_batch

def mat(x):return s.Matrix(x['matrix']).applyfunc(s.sympify)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver()

    def facts(self,p,v):return self.r._resolve(p,6,v)['payload']['facts']

    def test_all_variants(self):
        self.assertEqual(len(TARGETS),78)
        retained={'skew':'AL','line-plane-intersection':'AK','line-line-distance':'AP','triangle-area':'AO','plane-intersection-direction':'AQ','justify-skew':'AP'}
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
                            for prev,new in zip(old['rubric'],x['rubric']):
                                self.assertEqual(prev['marks'],new['marks']);self.assertTrue(new['criterion'].startswith(prev['criterion']))
                        else:self.assertEqual(item['revision'],'FM-16'+retained[p]);self.assertEqual(t,6)
                        for text in [x['question_latex'],x['final_answer_latex'],*x['worked_solution_latex']]:
                            self.assertEqual(text.count('$')%2,0)
                            self.assertEqual(text.count('\\begin{'),text.count('\\end{'))

    def test_ledger(self):
        rows=list(records(self.r));self.assertEqual(len(rows),252)
        self.assertEqual(validate_batch(rows,self.r)['statuses'],{'editorial_review_recorded':252})

    def test_invalid_targets(self):
        for key in [('skew',6,1),('point-line',True,1),('point-plane',2,True),('scalar-product',1,1)]:
            with self.assertRaises(ValueError):revise(*key)

    def test_point_line_minimum(self):
        t=s.symbols('t')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('point-line',v)
            P=s.Matrix([2*a,0,b]);H=mat(f[0]);D=s.Matrix([1,1,0]);Q=t*D
            self.assertEqual(H,a*D);self.assertEqual((P-H).dot(D),0)
            self.assertEqual(s.expand((P-Q).dot(P-Q)-s.sympify(f[1])**2),s.expand(2*(t-a)**2))
            self.assertEqual(set(map(s.sympify,f[2:])),{a-2,a+2})
            for T in (a-2,a+2):self.assertEqual((P-T*D).dot(P-T*D),2*a*a+b*b+8)

    def test_point_plane_circle(self):
        for v in (1,2,3):
            a,b=v+1,v+3;P=s.Matrix([a,b,0]);n=s.Matrix([1,2,2]);H=mat(self.facts('point-plane',v)[0]);rad=s.sympify(self.facts('point-plane',v)[1])
            self.assertEqual(P-H,n);self.assertEqual(n.dot(H),a+2*b-9)
            d=s.Matrix([2,-1,0]);Q=H+rad*d/s.sqrt(d.dot(d))
            self.assertEqual(n.dot(Q),n.dot(H));self.assertEqual(s.simplify((Q-P).dot(Q-P)),25)
            self.assertEqual(rad,4)

    def test_skew_planes(self):
        h,k=s.symbols('h k')
        for v in (1,2,3):
            a,b=v+1,v+3;f=list(map(s.sympify,self.facts('skew',v)));n=s.Matrix(f[:3]);D=s.Matrix([1,a,0]);E=s.Matrix([1,k,1]);P=s.Matrix([0,h,b]);X=s.Matrix(f[5:])
            self.assertEqual(n,D.cross(E));self.assertEqual(s.expand(n.dot(P)),f[3]);self.assertEqual(s.expand(f[3].subs(h,f[4])),0)
            self.assertEqual(X,-b*D);self.assertEqual((P-b*E).subs(h,f[4]),X)

    def test_line_line_minimum(self):
        h=s.symbols('h');D=s.Matrix([1,1,0]);E=s.Matrix([1,0,1]);t,u=s.symbols('t u')
        for v in (1,2,3):
            b=v+3;f=list(map(s.sympify,self.facts('line-line-distance',v)))
            for j,sign in enumerate((1,-1)):
                P=s.Matrix([h,0,sign*b]);W=f[2*j]*D-(P+f[2*j+1]*E)
                self.assertEqual(s.simplify(W.dot(D)),0);self.assertEqual(s.simplify(W.dot(E)),0)
                self.assertEqual(s.simplify((W.dot(W)-f[4+j]**2).subs(h,s.Symbol("h_real",real=True))),0)
                self.assertEqual(s.simplify(f[4+j].subs(h,sign*b)),0)
            self.assertEqual(s.det(s.Matrix([[D.dot(D),D.dot(E)],[D.dot(E),E.dot(E)]])),3)

    def test_triple_volume_boundaries(self):
        k=s.symbols('k');
        for v in (1,2,3):
            a,b=v+1,v+2;f=list(map(s.sympify,self.facts('triple-volume',v)));p=a*k*(k-b);B=s.Rational(a*b*b,4)
            self.assertEqual(s.expand(f[0]-p),0);self.assertEqual(f[1],B)
            for C,count in [(0,2),(B/2,4),(B,3),(B+1,2)]:
                roots=set(s.solve(p-C,k)+s.solve(p+C,k));self.assertEqual(sum(bool(x.is_real) for x in roots),count)

    def test_parallelogram_minimum(self):
        k,C=s.symbols('k C')
        for v in (1,2,3):
            a,b,c=v+1,v+3,2*v+3;f=list(map(s.sympify,self.facts('parallelogram-area',v)));U=s.Matrix([a,0,0]);V=s.Matrix([k,k-b,k+c]);w=U.cross(V);p=s.expand(w.dot(w))
            self.assertEqual(p,f[0]);self.assertEqual(s.diff(p,k).subs(k,f[1]),0);self.assertEqual(p.subs(k,f[1]),f[2])
            self.assertEqual(s.expand(p-f[2]),s.expand(2*a*a*(k-f[1])**2));self.assertEqual(s.simplify(f[3]-(C*C-f[2])/(2*a*a)),0)

    def test_common_plane_minimum(self):
        k,h,t=s.symbols('k h t')
        for v in (1,2,3):
            a=v+3;f=self.facts('plane-common-point',v);T=s.sympify(f[0]);X=mat(f[1]);P=s.Matrix([a,0,h-a]);D=s.Matrix([-1,1,1-k]);
            self.assertEqual((X-P-T*D).applyfunc(s.simplify),s.zeros(3,1));self.assertEqual(s.simplify(X.dot(D)),0)
            self.assertEqual(s.simplify(X.dot(X)-s.sympify(f[2])),0);self.assertEqual(s.expand(D.dot(D)),k*k-2*k+3)
            self.assertEqual(s.simplify(X[0]+X[1]),a);self.assertEqual(s.simplify(X[0]+k*X[1]+X[2]),h)

    def test_related_solids_boundaries(self):
        t,C=s.symbols('t C')
        for v in (1,2,3):
            a=s.Rational(v,v+1);f=list(map(s.sympify,self.facts('related-solids',v)));p=a*t*(1-t)
            self.assertEqual(f[0],a/4);self.assertEqual(s.expand(p-a/4),s.expand(-a*(t-s.Rational(1,2))**2));self.assertEqual(s.simplify(f[1]**2-(1-4*C/a)),0)
            self.assertEqual(set(s.solve(p,t)),{0,1});self.assertEqual(s.solve(p-f[0],t),[s.Rational(1,2)])

    def test_plane_line_branches(self):
        t,k,h=s.symbols('t k h')
        for v in (1,2,3):
            a=v+1;X,Y=map(mat,self.facts('plane-intersection-line',v));
            for Q,sub in [(X,{}),(Y,{h:0})]:
                self.assertEqual(s.simplify(Q[0]+Q[1]),a);self.assertEqual(s.simplify((k*Q[0]+Q[1]+h*Q[2]).subs(sub)),a+2)
            self.assertEqual(s.diff(Y,t),s.Matrix([0,0,1]));self.assertEqual(s.diff(X,t).subs(k,1),s.Matrix([1,-1,0]))
            self.assertNotEqual(a,a+2)

if __name__=='__main__':unittest.main()
