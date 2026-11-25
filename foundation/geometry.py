"""Bounded, dimension-driven original maths diagrams. No model-supplied SVG."""
import hashlib
import json

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
        # Dimensions are projected onto four different outside edges. This
        # avoids colliding text in a small removed corner.
        dimensions=[((0,h),(w,h),(0,1),w),((0,0),(0,h),(-1,0),h),
                    ((a,0),(w,0),(0,-1),b),((w,0),(w,c),(1,0),c)]
        alt='L-shaped floor. Outer rectangle and removed corner dimensions are labelled.'
        swap=bool(layout & 4)
        fx,fy=bool(layout & 1),bool(layout & 2)
    elif family == 'trapezium':
        w,h=2*(a+b),c
        top=2*a
        offset=(w-top)*(layout%4)/3
        vertices=[(offset,0),(offset+top,0),(w,h),(0,h)]
        dimensions=[((offset,0),(offset+top,0),(0,-1),top),((0,h),(w,h),(0,1),w),
                    ((w,0),(w,h),(1,0),h)]
        alt='Trapezium. Both parallel sides and the perpendicular height are labelled.'
        swap=False;fx=False;fy=bool(layout & 4)
    else:
        w,h,_=triangle_sides(a,b,c)
        vertices=[(0,0),(w,0),(w,h),(0,h)]
        # Explicit width and height in the question remain horizontal/vertical.
        dimensions=[((0,0),(w,0),(0,-1),w) if layout&2 else ((0,h),(w,h),(0,1),w),
                    ((w,0),(w,h),(1,0),h) if layout&4 else ((0,0),(0,h),(-1,0),h)]
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
    lines=[]; dimension_lines=[];labels=[];guides=[]
    if family=='l-shape':
        guides=[line(transform((a,0)),transform((w,0))),line(transform((w,0)),transform((w,c)))]
    elif family=='trapezium' and offset+top<w:
        guides=[line(transform((offset+top,0)),transform((w,0)))]
    for p,q,n,value in dimensions:
        x,y=transform(p);u,v=transform(q);nx,ny=normal(n)
        # Separate projection lines/ticks from the outline. Numbers always
        # use the actual model dimensions and never pixel measurements.
        P=(x+12*nx,y+12*ny);Q=(u+12*nx,v+12*ny)
        dimension_lines += [line(P,Q),line((x+3*nx,y+3*ny),(x+16*nx,y+16*ny)),
                            line((u+3*nx,v+3*ny),(u+16*nx,v+16*ny))]
        label=((x+u)/2+(34 if nx else 0)*nx,(y+v)/2+(27 if ny else 0)*ny+5)
        labels.append(rnd(label)+[f'{value} m'])
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
        labels.append(rnd((mid[0],mid[1]-15))+['brace'])
    return dict(kind='schematic',alt=alt,polygon=polygon,lines=lines,
                dimension_lines=dimension_lines,guides=guides,labels=labels)


def _edge(p,q):
    return sorted([tuple(round(x,2) for x in p),tuple(round(x,2) for x in q)])


def _segments(lines):
    return sorted(_edge(l[:2],l[2:]) for l in lines)


def _shape(d):
    p=d['polygon']
    return [sorted(_edge(p[i],p[(i+1)%len(p)]) for i in range(len(p))),_segments(d.get('lines',[]))]


def diagram_key(d):
    """Visual identity includes real dimensions, not unrelated question values."""
    return _digest([_shape(d),_segments(d.get('dimension_lines',[])),_segments(d.get('guides',[])),sorted(d['labels'])])


def shape_key(d):
    """Ignore dimension text; prefer distinct outlines and internal construction."""
    return _digest(_shape(d))


def _digest(value):
    return hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()[:24]
