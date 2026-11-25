"""Bounded, dimension-driven original maths diagrams. No model-supplied SVG."""
import hashlib
import json
from math import atan2, degrees, hypot

FAMILIES = ('l-shape', 'trapezium', 'pythagoras')
LAYOUTS = tuple(range(8))


def triangle_sides(a, b, c):
    # Keep the original 3-4-5 case for b % 4 == 3. Other parameters select
    # different exact triples; swap the legs for landscape/portrait variants.
    x, y, z = ((5, 12, 13), (8, 15, 17), (20, 21, 29), (3, 4, 5))[b % 4]
    if c % 2 == 0:
        x, y = y, x
    return a*x, a*y, a*z


def default_layout(a,b,c):
    return (a+2*b+3*c) % len(LAYOUTS)


def diagram(family,a,b,c,layout=None):
    if family not in FAMILIES:
        return None
    if any(type(v) is not int or v < 1 for v in (a,b,c)):
        raise ValueError('Invalid diagram dimensions')
    layout = default_layout(a,b,c) if layout is None else layout
    if type(layout) is not int or layout not in LAYOUTS:
        raise ValueError('Unsupported diagram layout')
    if family == 'l-shape':
        w,h=a+b,b+c
        vertices=[(0,0),(a,0),(a,c),(w,c),(w,h),(0,h)]
        # Each measurement starts on a REAL wall. Project the two notch
        # walls into the open corner and outside the bounding rectangle;
        # their witness lines still begin at the actual wall endpoints.
        dimensions=[('outer-width',(0,h),(w,h),(0,h),(w,h),(0,1),w),
                    ('outer-height',(0,0),(0,h),(0,0),(0,h),(-1,0),h),
                    ('notch-width',(a,c),(w,c),(a,0),(w,0),(0,-1),b),
                    ('notch-height',(a,0),(a,c),(w,0),(w,c),(1,0),c)]
        alt='L-shaped floor. Outer rectangle and removed corner dimensions are labelled.'
        swap=bool(layout & 4)
        fx,fy=bool(layout & 1),bool(layout & 2)
    elif family == 'trapezium':
        w,h=2*(a+b),c
        top=2*a
        offset=(w-top)*(layout%4)/3
        vertices=[(offset,0),(offset+top,0),(w,h),(0,h)]
        height_x=offset+top/2
        dimensions=[('short-base',(offset,0),(offset+top,0),(offset,0),(offset+top,0),(0,-1),top),
                    ('long-base',(0,h),(w,h),(0,h),(w,h),(0,1),w),
                    ('perpendicular-height',(height_x,0),(height_x,h),(w,0),(w,h),(1,0),h)]
        alt='Trapezium. Both parallel sides and the perpendicular height are labelled.'
        swap=False;fx=False;fy=bool(layout & 4)
    else:
        w,h,_=triangle_sides(a,b,c)
        vertices=[(0,0),(w,0),(w,h),(0,h)]
        # Explicit width and height in the question remain horizontal/vertical.
        wp,wq,wn=((0,0),(w,0),(0,-1)) if layout&2 else ((0,h),(w,h),(0,1))
        hp,hq,hn=((w,0),(w,h),(1,0)) if layout&4 else ((0,0),(0,h),(-1,0))
        dimensions=[('frame-width',wp,wq,wp,wq,wn,w),('frame-height',hp,hq,hp,hq,hn,h)]
        alt='Rectangular frame. Width, height, right angle and unknown diagonal brace are shown.'
        swap=fx=fy=False
    W,H=(h,w) if swap else (w,h)
    scale=min(310/W,168/H)
    left,y0=(480-W*scale)/2,(280-H*scale)/2
    def transform(p):
        x,y=p
        if fx:x=w-x
        if fy:y=h-y
        if swap:x,y=y,x
        return (left+x*scale,y0+y*scale)
    def normal(n):
        x,y=n
        if fx:x=-x
        if fy:y=-y
        return (y,x) if swap else (x,y)
    def rnd(p):return [round(v,4) for v in p]
    def line(p,q):return rnd(p)+rnd(q)
    polygon=[rnd(transform(p)) for p in vertices]
    lines=[]; dimension_lines=[];labels=[];guides=[];measurements=[]
    for name,p,q,project_p,project_q,n,value in dimensions:
        source_p,source_q=transform(p),transform(q)
        x,y=transform(project_p);u,v=transform(project_q);nx,ny=normal(n)
        P=(x+12*nx,y+12*ny);Q=(u+12*nx,v+12*ny)
        # Dimension line and end ticks are solid; witness lines are dashed.
        # For the height of a trapezium, witness lines begin on the right
        # base endpoints (on the same parallel lines as the actual height).
        witness_p,witness_q=source_p,source_q
        if name=='perpendicular-height':
            witness_p=transform((offset+top,0));witness_q=transform((w,h))
        main_index=len(dimension_lines);guide_index=len(guides)
        dimension_lines += [line(P,Q),line((P[0]-4*nx,P[1]-4*ny),(P[0]+4*nx,P[1]+4*ny)),
                            line((Q[0]-4*nx,Q[1]-4*ny),(Q[0]+4*nx,Q[1]+4*ny))]
        guides += [line(witness_p,P),line(witness_q,Q)]
        label=((x+u)/2+34*nx,(y+v)/2+27*ny+5)
        measurements.append(dict(role=name,value=value,unit='m',source=[rnd(source_p),rnd(source_q)],
                                 witnesses=[rnd(witness_p),rnd(witness_q)],normal=[nx,ny],
                                 line_index=main_index,guide_index=guide_index,label_index=len(labels)))
        labels.append(rnd(label)+[f'{value} m'])
    angles=[0]*len(labels)
    if family=='trapezium':
        x=offset+top/2
        p,q=transform((x,0)),transform((x,h))
        lines.append(line(p,q))
        # Mark the actual perpendicular at the bottom base, including when
        # the trapezium is inverted. Keep the marker inside the polygon.
        size=min(10, h*scale/3,top*scale/3)
        direction=-1 if q[1]>p[1] else 1
        lines.extend([line((q[0],q[1]+direction*size),(q[0]+size,q[1]+direction*size)),
                      line((q[0]+size,q[1]+direction*size),(q[0]+size,q[1]))])
    elif family=='pythagoras':
        if layout&1:
            start,end=(0,0),(w,h);corner=(w,0)
        else:
            start,end=(0,h),(w,0);corner=(0,0)
        p,q=transform(start),transform(end);r=transform(corner)
        lines.append(line(p,q))
        size=min(10,w*scale/4,h*scale/4)
        sx=-1 if corner[0]==w else 1;sy=1
        lines.extend([line((r[0]+sx*size,r[1]),(r[0]+sx*size,r[1]+sy*size)),
                      line((r[0]+sx*size,r[1]+sy*size),(r[0],r[1]+sy*size))])
        # A label offset from the diagonal, within the frame.
        mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
        dx,dy=q[0]-p[0],q[1]-p[1]; length=hypot(dx,dy)
        labels.append(rnd((mid[0]+12*dy/length,mid[1]-12*dx/length))+['brace'])
        angles.append(round(degrees(atan2(dy,dx)),3))
    result=dict(kind='schematic',alt=alt,polygon=polygon,lines=lines,
                dimension_lines=dimension_lines,guides=guides,labels=labels,label_angles=angles,
                measurements=measurements)
    validate_measurements(result,family,a,b,c,layout)
    return result


def validate_measurements(d,family,a,b,c,layout):
    """Fail closed if a label, wall, witness or perpendicular is inconsistent.

    The expected values come from the mathematical parameters, not the SVG.
    A length label may be projected outside the shape, but its witnesses must
    connect the correct endpoints and its span must equal the measured edge.
    """
    if family=='l-shape':
        expected={'outer-width':a+b,'outer-height':b+c,'notch-width':b,'notch-height':c}
        width,height=(b+c,a+b) if layout&4 else (a+b,b+c)
        wall_indices={'outer-width':(5,4),'outer-height':(0,5),'notch-width':(2,3),'notch-height':(1,2)}
    elif family=='trapezium':
        expected={'short-base':2*a,'long-base':2*(a+b),'perpendicular-height':c}
        width,height=2*(a+b),c
        wall_indices={'short-base':(0,1),'long-base':(3,2)}
    elif family=='pythagoras':
        width,height,_=triangle_sides(a,b,c)
        expected={'frame-width':width,'frame-height':height}
        wall_indices={'frame-width':(0,1) if layout&2 else (3,2),
                      'frame-height':(1,2) if layout&4 else (0,3)}
    else:
        raise ValueError('Unknown measurement family')
    poly=d['polygon']; measures=d['measurements']
    def need(ok):
        if not ok: raise ValueError('Inconsistent diagram measurement or label')
    def near(x,y):return abs(x-y)<0.002
    def same(p,q):return all(near(x,y) for x,y in zip(p,q))
    def dot(p,q):return sum(x*y for x,y in zip(p,q))
    def sub(p,q):return [x-y for x,y in zip(p,q)]
    def edge_exists(p,q):return any((same(p,u) and same(q,v)) or (same(q,u) and same(p,v)) for u,v in zip(poly,poly[1:]+poly[:1]))
    W=max(p[0] for p in poly)-min(p[0] for p in poly)
    H=max(p[1] for p in poly)-min(p[1] for p in poly)
    scale=W/width
    need(near(H,height*scale))
    need(len(measures)==len(expected) and {m['role'] for m in measures}==set(expected))
    need(len(d['dimension_lines'])==3*len(measures) and len(d['guides'])==2*len(measures))
    need(sorted(m['line_index'] for m in measures)==list(range(0,3*len(measures),3)))
    need(sorted(m['guide_index'] for m in measures)==list(range(0,2*len(measures),2)))
    need(sorted(m['label_index'] for m in measures)==list(range(len(measures))))
    for m in measures:
        role=m['role']; value=m['value']; p,q=m['source']; n=m['normal']; wp,wq=m['witnesses']
        need(value==expected[role] and m['unit']=='m')
        need(near(hypot(*sub(q,p)),value*scale) and near(dot(sub(q,p),n),0))
        if role=='perpendicular-height':
            need(near(p[0],q[0]) and near(abs(q[1]-p[1]),H))
            need(same(d['lines'][0][:2],p) and same(d['lines'][0][2:],q))
            need(near(wp[1],p[1]) and near(wq[1],q[1]))
            need(same(wp,poly[1]) and same(wq,poly[2]))
        else:
            i,j=wall_indices[role]
            need(same(p,poly[i]) and same(q,poly[j]))
            need(edge_exists(p,q) and same(wp,p) and same(wq,q))
        # The named wall determines horizontal/vertical direction, including
        # rotations/reflections; equal numeric values do not swap the roles.
        if family=='l-shape':
            horizontal=('width' in role) != bool(layout&4)
            need(near(p[1],q[1]) if horizontal else near(p[0],q[0]))
            # The notch's two walls must meet at the concave vertex (index 2).
            if role.startswith('notch-'): need(same(p,poly[2]) or same(q,poly[2]))
        if family=='pythagoras': need(near(p[1],q[1]) if role=='frame-width' else near(p[0],q[0]))
        if role.endswith('-base'): need(near(p[1],q[1]))
        l=d['dimension_lines'][m['line_index']]; P,Q=l[:2],l[2:]
        need(same(sub(Q,P),sub(q,p)))
        # Dimension lines sit beyond the outline in the measured direction.
        need(dot(P,n)>max(dot(v,n) for v in poly))
        for endpoint,tick in zip((P,Q),d['dimension_lines'][m['line_index']+1:m['line_index']+3]):
            need(same(tick[:2],[x-4*y for x,y in zip(endpoint,n)]) and same(tick[2:],[x+4*y for x,y in zip(endpoint,n)]))
        for start,end,g in zip((wp,wq),(P,Q),d['guides'][m['guide_index']:m['guide_index']+2]):
            need(same(g[:2],start) and same(g[2:],end))
            delta=sub(end,start)
            need(dot(delta,n)>0 and near(dot(delta,sub(q,p))/hypot(*sub(q,p)),0))
        x,y,text=d['labels'][m['label_index']]
        need(text==f'{value} m')
        # Text is centred on the dimension span, never a neighbouring wall.
        label=[x,y-5]; mid=[(P[0]+Q[0])/2,(P[1]+Q[1])/2]
        need(near(dot(sub(label,mid),sub(Q,P))/hypot(*sub(Q,P)),0) and dot(sub(label,mid),n)>0)
    return True


def _edge(p,q):
    return sorted([tuple(round(x,2) for x in p),tuple(round(x,2) for x in q)])


def _segments(lines):
    return sorted(_edge(l[:2],l[2:]) for l in lines)


def _shape(d):
    p=d['polygon']
    return [sorted(_edge(p[i],p[(i+1)%len(p)]) for i in range(len(p))),_segments(d.get('lines',[]))]


def diagram_key(d):
    """Visual identity includes real dimensions, not unrelated question values."""
    return _digest([_shape(d),_segments(d.get('dimension_lines',[])),_segments(d.get('guides',[])),sorted(zip(d['labels'],d.get('label_angles',[0]*len(d['labels']))))])


def shape_key(d):
    """Ignore dimension text; prefer distinct outlines and internal construction."""
    return _digest(_shape(d))


def _digest(value):
    return hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()[:24]
