"""Original rectilinear floor problems. Dimensions are tied to named wall endpoints.

Widths/heights are integer metres. Independent unit-cell and edge-count checks
verify decomposition, perimeter and purchase arithmetic; never infer from pixels.
"""
from math import hypot, ceil


def profile(level,a,b,c):
    # Keep ratios readable and mental arithmetic realistic, independently of
    # the old parameter ranges. The hard cases include a U, a raised middle,
    # and two distinct staircase profiles.
    widths=[6+a%5, 6+b%5]
    h=5+c%4
    if level=='easy': return widths,[h,h+3+b%3]
    if level=='standard': return widths,[h+3+a%3,h]
    widths.append(6+c%5)
    rise=3+a%3; extra=3+b%3
    heights=([h+rise,h,h+extra], [h,h+rise,h], [h+rise+extra,h+extra,h], [h,h+rise,h+rise+extra])[a%4]
    return widths,heights


def model(level,a,b,c):
    widths,heights=profile(level,a,b,c)
    W,H=sum(widths),max(heights)
    xs=[0]
    for w in widths: xs.append(xs[-1]+w)
    top=[H-h for h in heights]
    polygon=[(0,H),(0,top[0])]
    for i in range(len(widths)):
        polygon.append((xs[i+1],top[i]))
        if i+1<len(widths): polygon.append((xs[i+1],top[i+1]))
    polygon.append((W,H))
    # Source endpoints on the actual solid outline, not on imaginary walls.
    walls=[]
    def wall(role,p,q,n,value,outer=True): walls.append((role,p,q,n,value,outer))
    if level!='easy': wall('overall-width',(0,H),(W,H),(0,1),W)
    for i,w in enumerate(widths):
        if level=='easy' or (level=='standard' and i==0) or (level=='challenge' and i!=1):
            wall(f'strip-{i+1}-width',(xs[i],top[i]),(xs[i+1],top[i]),(0,-1),w)
    wall('left-height',(0,H),(0,top[0]),(-1,0),heights[0])
    wall('right-height',(W,top[-1]),(W,H),(1,0),heights[-1])
    if level=='challenge':
        # The first riser determines the middle strip height from the first
        # strip height. The student reads whether it is a rise or a recess.
        p,q=(xs[1],top[0]),(xs[1],top[1]); n=(1,0) if top[1]>top[0] else (-1,0)
        wall('first-step-height',p,q,n,abs(heights[1]-heights[0]),False)
    return widths,heights,polygon,walls


def diagram(level,a,b,c,layout=0):
    widths,heights,poly,walls=model(level,a,b,c)
    W,H=sum(widths),max(heights)
    # Reflections are safe because every role, endpoint and normal transforms
    # together. Bit 2 selects a quarter-turn for additional silhouettes.
    swap=bool(layout&4); fx=bool(layout&1); fy=bool(layout&2)
    w,h=(H,W) if swap else (W,H)
    scale=min(300/w,148/h); left,top=(480-w*scale)/2,(280-h*scale)/2
    def point(p):
        x,y=p
        if fx:x=W-x
        if fy:y=H-y
        if swap:x,y=y,x
        return [left+x*scale,top+y*scale]
    def normal(n):
        x,y=n
        if fx:x=-x
        if fy:y=-y
        return (y,x) if swap else (x,y)
    def r(p): return [round(x,4) for x in p]
    def line(p,q): return r(p)+r(q)
    def dot(p,q): return sum(x*y for x,y in zip(p,q))
    polygon=[r(point(p)) for p in poly]
    dimensions=[]; guides=[]; labels=[]; measures=[]; lines=[]
    # All width labels use the same outer dimension lane, with witnesses
    # extending from their actual edges. Riser labels sit in the recess.
    for role,p,q,n,value,outer in walls:
        p,q=point(p),point(q); nx,ny=normal(n); n=(nx,ny)
        distance=(max(dot(v,n) for v in polygon)-dot(p,n)+12) if outer else 9
        P=[p[0]+distance*nx,p[1]+distance*ny]; Q=[q[0]+distance*nx,q[1]+distance*ny]
        i=len(dimensions); j=len(guides); k=len(labels)
        dimensions += [line(P,Q),line([P[0]-3*nx,P[1]-3*ny],[P[0]+3*nx,P[1]+3*ny]),line([Q[0]-3*nx,Q[1]-3*ny],[Q[0]+3*nx,Q[1]+3*ny])]
        guides += [line(p,P),line(q,Q)]
        # Use vertically oriented text on vertical dimension lines; this
        # avoids collision with nearby steps or adjoining dimension spans.
        vertical=abs(P[0]-Q[0])<.001
        offset=13 if vertical else 13
        mid=[(P[0]+Q[0])/2+offset*nx,(P[1]+Q[1])/2+offset*ny]
        labels.append(r(mid)+[f'{value} m'])
        measures.append(dict(role=role,value=value,source=[r(p),r(q)],normal=list(n),line_index=i,guide_index=j,label_index=k))
    # For the easy level, a visible decomposition line provides scaffolding.
    if level=='easy':
        x=widths[0]; lines.append(line(point((x,H-min(heights))),point((x,H))))
    # Label rotation is handled in the renderer, use a centred baseline.
    angles=[-90 if abs(dimensions[m['line_index']][0]-dimensions[m['line_index']][2])<.001 else 0 for m in measures]
    d=dict(kind='schematic',alt='Rectilinear floor plan with perpendicular adjoining walls.',polygon=polygon,lines=[],dimension_lines=dimensions,guides=guides,labels=labels,label_angles=angles,measurements=measures,centre_labels=True,construction_lines=lines)
    validate_diagram(d,level,a,b,c,layout)
    return d


def validate_diagram(d,level,a,b,c,layout):
    widths,heights,poly,walls=model(level,a,b,c)
    W,H=sum(widths),max(heights)
    swap=bool(layout&4); fx=bool(layout&1); fy=bool(layout&2)
    w,h=(H,W) if swap else (W,H); scale=min(300/w,148/h)
    left,top=(480-w*scale)/2,(280-h*scale)/2
    def point(p):
        x,y=p
        if fx:x=W-x
        if fy:y=H-y
        if swap:x,y=y,x
        return [left+x*scale,top+y*scale]
    def near(p,q):return len(p)==len(q) and all(abs(x-y)<.003 for x,y in zip(p,q))
    def sub(p,q):return [x-y for x,y in zip(p,q)]
    def dot(p,q):return sum(x*y for x,y in zip(p,q))
    def require(ok):
        if not ok: raise ValueError('Composite geometry measurement mismatch')
    require(len(d['polygon'])==len(poly) and all(near(x,point(y)) for x,y in zip(d['polygon'],poly)))
    require(len(d['measurements'])==len(walls) and len(d['labels'])==len(walls))
    require(len(d['dimension_lines'])==3*len(walls) and len(d['guides'])==2*len(walls))
    for i,((role,p,q,n,value,outer),m) in enumerate(zip(walls,d['measurements'])):
        p,q=point(p),point(q)
        nx,ny=n
        if fx:nx=-nx
        if fy:ny=-ny
        if swap:nx,ny=ny,nx
        n=[nx,ny]
        require(m['role']==role and m['value']==value and near(m['source'][0],p) and near(m['source'][1],q) and near(m['normal'],n))
        require((m['line_index'],m['guide_index'],m['label_index'])==(3*i,2*i,i))
        l=d['dimension_lines'][3*i]; P,Q=l[:2],l[2:]
        require(near(sub(Q,P),sub(q,p)) and abs(hypot(*sub(q,p))-value*scale)<.003)
        require(dot(sub(P,p),n)>0 and abs(dot(sub(P,p),sub(q,p)))<.1)
        for source,end,guide in zip((p,q),(P,Q),d['guides'][2*i:2*i+2]):
            require(near(guide[:2],source) and near(guide[2:],end))
        for end,tick in zip((P,Q),d['dimension_lines'][3*i+1:3*i+3]):
            require(near(tick[:2],[end[0]-3*nx,end[1]-3*ny]) and near(tick[2:],[end[0]+3*nx,end[1]+3*ny]))
        x,y,text=d['labels'][i]; mid=[(P[0]+Q[0])/2+13*nx,(P[1]+Q[1])/2+13*ny]
        require(text==f'{value} m' and near([x,y],mid))
        require(d['label_angles'][i]==(-90 if abs(P[0]-Q[0])<.001 else 0))
        require(15<=x<=465 and 15<=y<=265)
    # Verify the scaled polygon area against the independent cell model.
    cells=cell_model(widths,heights); p=d['polygon']; area=abs(sum(x*v-u*y for (x,y),(u,v) in zip(p,p[1:]+p[:1])))/2/scale**2
    require(abs(area-len(cells))<.01)
    return True


def cell_model(widths,heights):
    cells=set(); offset=0
    for width,height in zip(widths,heights):
        cells.update((x,y) for x in range(offset,offset+width) for y in range(height));offset+=width
    return cells


def answers(level,a,b,c):
    w,h=profile(level,a,b,c); area=sum(x*y for x,y in zip(w,h))
    if level=='easy': return (area,)
    if level=='standard': return (area,area*(2+c%5))
    perimeter=2*sum(w)+h[0]+h[-1]+sum(abs(x-y) for x,y in zip(h,h[1:]))
    coverage=3+b%4; packs=(area+coverage-1)//coverage; cost=packs*(4+c%5)
    return area,perimeter,packs,cost


def validate(level,a,b,c,answer):
    w,h=profile(level,a,b,c); cells=cell_model(w,h); area=len(cells)
    if not isinstance(answer,tuple):return False
    if level=='easy': return answer==(area,)
    if level=='standard':return len(answer)==2 and answer[0]==area and answer[1]==sum([2+c%5]*area)
    if len(answer)!=4:return False
    perimeter=sum((x+dx,y+dy) not in cells for x,y in cells for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
    A,P,n,C=answer; coverage=3+b%4
    return A==area and P==perimeter and (n-1)*coverage<area<=n*coverage and C==n*(4+c%5)


def question(level,a,b,c,layout):
    w,h=profile(level,a,b,c); ans=answers(level,a,b,c); A=ans[0]
    if not validate(level,a,b,c,ans):raise ValueError('Composite answer check failed')
    context='The diagram shows a floor plan. All adjoining walls are perpendicular. Use the labelled measurements, not a ruler.'
    decomposition=' + '.join(f'{x} x {y}' for x,y in zip(w,h))
    if level=='easy':
        q=context+' The internal line splits the floor into two rectangles. Find the total floor area.'
        steps=[f'Area of the two rectangles: {decomposition} = {A} m^2.']
        rubric=['M1: find the area of each rectangle.','A1: correct total area.']; answer=f'{A} m^2'
    elif level=='standard':
        rate=2+c%5
        q=context+f' Flooring costs £{rate} per square metre. (a) Find the floor area. (b) Find the total flooring cost.'
        steps=[f'Missing width = {sum(w)} - {w[0]} = {w[1]} m.',f'Area = {decomposition} = {A} m^2.',f'Cost = {A} x £{rate} = £{ans[1]}.']
        rubric=['(a) M1: deduce the missing width or equivalent decomposition.','(a) M1: calculate and combine non-overlapping areas.','(a) A1: correct area.','(b) A1: correct cost; follow through a valid area.'];answer=f'(a) {A} m^2; (b) £{ans[1]}'
    else:
        coverage=3+b%4; rate=4+c%5; _,P,n,C=ans
        q=context+f' One pack of flooring covers {coverage} m^2 and costs £{rate}. Offcuts may be reused; packs are sold whole. (a) Find the floor area. (b) Find the perimeter of the floor. (c) Find the minimum number of packs and their total cost.'
        sign='+' if h[1]>h[0] else '-'
        steps=[f'Missing width = {sum(w)} - {w[0]} - {w[2]} = {w[1]} m.',f'Middle strip height = {h[0]} {sign} {abs(h[1]-h[0])} = {h[1]} m.',f'Area = {decomposition} = {A} m^2.',f'Perimeter = 2 x {sum(w)} + {h[0]} + {h[-1]} + {abs(h[1]-h[0])} + {abs(h[2]-h[1])} = {P} m.',f'{A} / {coverage}: {n-1} packs are insufficient, so buy {n} packs.',f'Cost = {n} x £{rate} = £{C}.']
        rubric=['(a) M1: infer missing width and middle height or equivalent valid method.','(a) M1: calculate areas of non-overlapping components.','(a) A1: correct total area.','(b) M1: sum all external lengths, including both steps.','(b) A1: correct perimeter.','(c) M1: divide area by pack coverage.','(c) A1: round up to the minimum whole packs.','(c) A1: correct cost from packs; follow through a valid pack count.'];answer=f'(a) {A} m^2; (b) {P} m; (c) {n} packs, £{C}'
    return dict(question=q,answer=answer,solution=steps,rubric=rubric,marks=len(rubric),diagram=diagram(level,a,b,c,layout),difficulty_features=['guided decomposition and direct area','deduce an unlabelled width and calculate cost','deduce two lengths, choose decomposition, perimeter, round up packs and cost'][('easy','standard','challenge').index(level)])
