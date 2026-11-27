"""Preservation and independent boundary checks for lines, planes and angles."""
import unittest
import sympy as s
from active_difficulty import Resolver
from difficulty_revision_bg import BANKS,TARGETS,base,revise
from marking_design_bg import records
from marking_review import inventory_entry
from marking_batch import validate_batch

def mat(x):return s.Matrix(x['matrix']).applyfunc(s.sympify)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=Resolver()

    def test_all_variants(self):
        self.assertEqual(len(TARGETS),65)
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
                        else:self.assertEqual(item['revision'],'FM-16AO');self.assertEqual((p,t),('line-plane-angle',6))
                        for text in [x['question_latex'],x['final_answer_latex'],*x['worked_solution_latex']]:
                            self.assertEqual(text.count('$')%2,0)
                            self.assertEqual(text.count('\\begin{'),text.count('\\end{'))

    def test_ledger(self):
        rows=list(records(self.r));self.assertEqual(len(rows),198)
        self.assertEqual(validate_batch(rows,self.r)['statuses'],{'editorial_review_recorded':198})

    def test_invalid_target(self):
        for key in [('line-plane-angle',6,1),('vector-plane',True,1),('zero-direction',2,True),('scalar-product',1,1)]:
            with self.assertRaises(ValueError):revise(*key)

    def facts(self,p,v):return self.r._resolve(p,6,v)['payload']['facts']

    def test_coincident_points_perpendicular_directions(self):
        k,h=s.symbols('k h')
        for v in (1,2,3):
            a,b=v+1,v+3;n=s.Matrix([a,b,0]);f=self.facts('vector-line-equation',v)
            self.assertEqual(s.sympify(f[0]),n.dot(s.Matrix([k,h,0])))
            U,V=map(mat,f[1:]);self.assertEqual(n.dot(U),0);self.assertEqual(n.dot(V),0);self.assertEqual(s.Matrix.hstack(U,V).rank(),2)
            self.assertEqual(s.Matrix.hstack(U,V,n).rank(),3)
            self.assertEqual(n.dot(s.Matrix([b,-a,0])),0);self.assertNotEqual(n.dot(s.Matrix([1,0,0])),0)

    def test_cartesian_zero_direction_branches(self):
        k,h,p,t=s.symbols('k h p t')
        for v in (1,2,3):
            a,b=v+1,v+2;f=self.facts('cartesian-line',v);X=mat(f[0]);self.assertEqual(X,s.Matrix([a+(h-b)/k,h,1]))
            self.assertEqual(X.subs({k:2,h:b+6}),s.Matrix([a+3,b+6,1]))
            self.assertEqual(s.Matrix([a,b,1])+t*s.Matrix([1,0,0]),s.Matrix([a+t,b,1]))
            a,b,c=v+1,v+3,2*v+5;X,P,L=map(mat,self.facts('zero-direction',v));self.assertEqual(P,s.Matrix([a,b,c]));self.assertEqual(L,P+t*s.Matrix([0,k,0]));self.assertEqual(X,P+(p/h)*s.Matrix([0,k,h]))
            for K,H,J in [(0,2,4),(3,2,4),(3,0,0),(3,0,4),(0,0,0),(0,0,4)]:
                d=s.Matrix([0,K,H]);self.assertEqual(d==s.zeros(3,1),K==H==0)
                if H:self.assertEqual(X.subs({k:K,h:H,p:J}),P+s.Rational(J,H)*d)
                else:self.assertEqual((P+t*d)[2]==c+J,J==0)

    def test_plane_rank_cases(self):
        k,h=s.symbols('k h')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('vector-plane',v);P=s.Matrix([0,k,h]);Q=s.Matrix([0,b*b*h,k]);U=s.Matrix([a,0,0])
            self.assertEqual(s.sympify(f[0]),s.det(s.Matrix([[k,b*b*h],[h,k]])))
            for K,H,rank in [(0,0,1),(b,1,2),(-b,1,2),(0,1,3),(1,0,3)]:
                cols=s.Matrix.hstack(U,P.subs({k:K,h:H}),Q.subs({k:K,h:H}));self.assertEqual(cols.rank(),rank)
                if rank==2:
                    W=mat(f[1 if K>0 else 2]);self.assertEqual(s.Matrix.hstack(U,W,*cols.columnspace()).rank(),2)
            f=self.facts('plane-cartesian',v);N=mat(f[0]);U=s.Matrix([1,-a,0]);self.assertEqual(N.dot(U),0);self.assertEqual(N.dot(s.Matrix([0,h,k])),0)
            self.assertEqual(s.Matrix.hstack(mat(f[2]),mat(f[3])).rank(),2)
            self.assertEqual(N.subs({h:0,k:0}),s.zeros(3,1))

    def test_fixed_normal_component(self):
        h,k,t=s.symbols('h k t')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('plane-normal',v);U=s.Matrix([a,1,0]);V=s.Matrix([h,k,b*k]);N=mat(f[0]);self.assertEqual(N.dot(U),0);self.assertEqual(s.simplify(N.dot(V)),0)
            for H,K in [(1,1),(0,2),(-3,-2)]:
                self.assertEqual(s.Matrix.hstack(U,V.subs({h:H,k:K})).rank(),2);self.assertEqual(N.subs({h:H,k:K})[0],1)
            self.assertEqual(s.Matrix.hstack(U,V.subs({h:1,k:0})).rank(),2)
            self.assertEqual(mat(f[2]).dot(U),0);self.assertEqual(mat(f[2]).dot(V.subs({h:1,k:0})),1)
            self.assertEqual(V.subs({h:0,k:0}),s.zeros(3,1))

    def test_oriented_normal_and_degeneracy(self):
        k,h=s.symbols('k h')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('cross-normal',v);U=s.Matrix([1,k,a*k]);V=s.Matrix([h,b,a*b]);C=U.cross(V);g=s.sympify(f[0]);W=s.Matrix([0,-a,1]);self.assertEqual(C,g*W)
            self.assertEqual(mat(f[1]),W/W.norm());self.assertEqual(mat(f[2]),-W/W.norm())
            for K,H in [(1,b-1),(1,b),(1,b+1),(-1,-b)]:
                X,Y=U.subs(k,K),V.subs(h,H);self.assertEqual(s.Matrix.hstack(X,Y).rank(),1 if K*H==b else 2)
                if K*H!=b:self.assertEqual(X.cross(Y)/X.cross(Y).norm(),mat(f[1 if K*H<b else 2]))

    def test_unit_normal_plane_counts(self):
        h=s.Symbol('h')
        for v in (1,2,3):
            a,b=v+1,v+3;f=self.facts('normal-dot-plane',v);P=s.Matrix([a,0,0]);Q=s.Matrix([0,b,0]);N,M=map(mat,f[:2]);
            for X in (N,M):self.assertEqual(s.simplify(X.dot(X)),1);self.assertEqual(s.simplify(X.dot(Q-P)),0)
            self.assertEqual(s.simplify(N.dot(P)-s.sympify(f[2])),0)
            for H,count in [(0,1),(1,1),(-1,1),(s.Rational(1,2),2),(s.Rational(-1,2),2)]:
                X,Y=N.subs(h,H),M.subs(h,H);self.assertEqual(1 if X==Y or X==-Y else 2,count)
            self.assertLess(1-2**2,0)

    def test_line_angle_degree_and_discriminant(self):
        k,t=s.symbols('k t')
        for v in (1,2,3):
            a,b=v+1,v+2;f=self.facts('line-line-angle',v);F,T,L=map(s.sympify,f[:3]);self.assertEqual(s.expand(F),s.expand(k*k-t*(k*k+a*a+(k-b)**2)))
            self.assertEqual(s.solve(F.subs(t,s.Rational(1,2)),k),[L]);self.assertEqual(s.discriminant(F,k).subs(t,T),0)
            for x,n in [(0,1),(s.Rational(1,4),2),(s.Rational(1,2),1),((T+s.Rational(1,2))/2,2),(T,1),((T+1)/2,0),(1,0)]:
                roots=s.Poly(F.subs(t,x),k).real_roots();self.assertEqual(len(set(roots)),n)
                for z in set(roots):self.assertEqual(s.simplify(z*z/(z*z+a*a+(z-b)**2)-x),0)

    def test_plane_and_line_plane_angle_thresholds(self):
        c,p,q=s.symbols('c p q')
        for v in (1,2,3):
            a=v+1;f=self.facts('plane-plane-angle',v);R,S=map(s.sympify,f[-2:]);self.assertEqual(s.simplify(R-a*a*(1-c)/(1+c)),0);self.assertEqual(s.simplify(S-a*a*(1+c)/(1-c)),0)
            for C,count in [(0,2),(s.Rational(1,3),4),(1,1)]:
                squares=[R.subs(c,C)]+([S.subs(c,C)] if C!=1 else []);roots={sgn*s.sqrt(z) for z in squares for sgn in (-1,1)};self.assertEqual(len(roots),count)
                for z in roots:self.assertEqual(s.simplify(abs(a*a-z*z)/(a*a+z*z)),C)
            f=self.facts('line-plane-angle',v);D,L,X,Z=map(s.sympify,f[:4]);self.assertEqual(D,1-p*p-q*q);self.assertEqual(s.simplify(X*X+a*a+Z*Z-L*L),0)
            for P,Q,count in [(0,0,1),(s.Rational(1,2),0,2),(0,s.Rational(1,2),2),(s.Rational(1,2),s.Rational(1,2),4),(0,1,0),(1,1,0)]:
                d=D.subs({p:P,q:Q});roots=set() if d<=0 else {(i*X.subs({p:P,q:Q}),j*Z.subs({p:P,q:Q})) for i in (-1,1) for j in (-1,1)};self.assertEqual(len(roots),count)
                for x,z in roots:
                    l=s.sqrt(x*x+a*a+z*z);self.assertEqual(s.simplify(abs(x)/l),P);self.assertEqual(s.simplify(abs(z)/l),Q)

if __name__=='__main__':unittest.main(verbosity=2)
