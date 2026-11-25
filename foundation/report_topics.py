"""Derive provisional whole-question topic evidence from examiner reports.
Original report text is transient; labels are editorial, never grading evidence.
"""
import argparse, csv, hashlib, re, sqlite3, subprocess
from pathlib import Path

HEAD = re.compile(r'^\s*Assessment Unit\s+M?([1-8])([12])?\s+(Foundation|Higher) Tier(?:\s+(Non-Calculator|Calculator))?\s*$',re.I)
Q = re.compile(r'^\s*Q\s*(\d{1,2})\b\s*(.*)$')
SCHEMA = '''CREATE TABLE IF NOT EXISTS examiner_skill_evidence(
 report_sha TEXT NOT NULL, unit TEXT NOT NULL, component TEXT NOT NULL, num INTEGER NOT NULL,
 skill TEXT NOT NULL REFERENCES skills, status TEXT NOT NULL,
 PRIMARY KEY(report_sha,unit,component,num,skill),
 FOREIGN KEY(report_sha,unit,component,num) REFERENCES examiner_anchors);
 CREATE INDEX IF NOT EXISTS examiner_skill_lookup ON examiner_skill_evidence(unit,skill);'''
# Prefer precise phrases, not generic comments about arithmetic or accuracy.
# The first available skill is selected, with native/inherited IDs resolved explicitly.
RULES = [
 ('pictogram|pie chart|bar chart|line graph|frequency diagram|stem and leaf', ['charts']),
 ('scatter graph|scatter diagram|scatter plot|correlation|line of best fit', ['m2-scatter','correlation']),
 ('two-way table|two way table|frequency table|venn diagram', ['organise-data']),
 ('three[- ]circle venn|three[- ]set venn', ['m2-venn-three']),
 ('mean|median|modal|mode of|the mode|the range|range and|range of the data', ['averages']),
 ('modal class|median class|grouped frequency|estimated mean|estimate the mean', ['m2-grouped-statistics']),
 ('random sample|biased sample|questionnaire|sampling|representative sample', ['survey']),
 ('negative number|negative temperature|negative integer|signed number|bank balances', ['integers']),
 ('decimal place value|place value|decimal point|money notation', ['place-value']),
 ('rounding|nearest hundred|nearest thousand|decimal place|round correctly', ['rounding']),
 ('significant figure', ['m2-significant-figures','rounding']),
 ('recurring decimal', ['m2-recurring-decimals']),
 ('prime number|cube number|square number|square root|cube root|factor and multiple|factors and multiples', ['number-properties']),
 ('highest common factor|lowest common multiple|prime factorisation|hcf|lcm', ['m2-factors','number-properties']),
 ('fraction|numerator|denominator', ['fractions']),
 ('mixed number|improper fraction', ['m2-mixed-fractions','fractions']),
 ('percentage|percent', ['percentage']),
 ('compound interest|successive discounts|repeated percentage', ['m2-repeated-change','percentage']),
 ('simple interest|wages|hourly rate|profit|loss|vat|sale price|discount|cost price', ['finance']),
 ('order of precedence|order of operations|bidmas|bodmas', ['calculator']),
 ('algebraic notation|algebraic expression|algebraic convention', ['algebra-language']),
 ('collecting like terms|like terms|simplifying the expression|simplify the expression', ['simplify']),
 ('multiply out|multiplying out|expand the bracket|expanding the bracket', ['m2-expand','simplify']),
 ('factorise|factorising|factorisation|common factor', ['m2-factorise','simplify']),
 ('substitut(?:e|ion|ing)|use the formula|given formula', ['formula']),
 ('linear equation|solving the equation|solve the equation', ['m2-equations','equations']),
 ('midpoint|mid-point', ['m2-midpoint-length']),
 ('coordinate|co-ordinate|straight line graph|linear graph', ['coordinates']),
 ('gradient|intercept', ['m2-gradient']),
 ('right angle|vertically opposite|alternate angle|corresponding angle|angles at a point|angles on a straight line', ['angles']),
 ('interior angle|exterior angle|angle sum of a polygon|polygon angle sum', ['m6-polygon-angles','m5-polygon-angles','angles']),
 ('triangle angle sum|angle sum of a triangle|isosceles triangle', ['m5-polygon-angles','angles']),
 ('rotational symmetry|line of symmetry|line symmetry|perpendicular sides|parallel sides', ['shape']),
 ('hexagon|trapezium|parallelogram|rhombus|quadrilateral', ['polygons']),
 ('radius|diameter|circumference|area of a circle', ['circles']),
 ('net of a cube|nets of a cube|elevation|plan view|vertices|faces and edges', ['solids']),
 ('perimeter|volume of a cuboid|area of a rectangle|area of a triangle|surface area', ['area']),
 ('area of a trapezium|area of a parallelogram|area of a rhombus', ['m2-plane-area','area']),
 ('composite area|compound shape|composite shape', ['m2-composite-area','area']),
 ('volume of a prism|volume of the prism|cross-sectional area', ['m2-prism-volume']),
 ('pythagoras|hypotenuse', ['m2-pythagoras']),
 ('metric conversion|metric units|millimetres|centimetres|kilograms|litres|tonnes', ['metric']),
 ('measuring the angle|measured length|use a protractor|use a ruler|drawn within tolerance', ['drawing']),
 ('average speed|fuel economy|miles per hour|kilometres per hour', ['rates']),
 ('density|mass per unit volume', ['m2-density']),
 ('estimation|estimate the calculation|estimate the answer', ['m5-estimation','rounding']),
 ('ratio|sharing in the ratio', ['m5-ratio']),
 ('best buy|best value|exchange rate|direct proportion|unit price', ['m5-proportion']),
 ('sequence|term-to-term|triangular number', ['m5-sequences']),
 ('conversion graph|distance-time graph|travel graph', ['m5-travel-graphs']),
 ('imperial|inches|gallons', ['m5-imperial']),
 ('scale drawing|map scale|scale of the map', ['m5-scale']),
 ('rotation|reflection|translation|transformation|reflecting|rotating', ['m6-transforms','m5-transformations']),
 ('enlargement|enlarged|scale factor', ['m6-enlargement','m5-transformations']),
 ('probability', ['m5-probability']),
 ('mutually exclusive|complementary probability|sum of the probabilities', ['m5-complement','m5-probability']),
 ('expected frequency|how many would you expect', ['m5-expectation']),
 ('sample space|possible outcomes|systematic list', ['m6-outcomes','m5-outcomes']),
 ('binary|base two', ['m6-binary']),
 ('index law|indices', ['m6-algebra-indices','m2-index-laws']),
 ('trial and improvement', ['m6-trial-improvement']),
 ('inequality|inequalities', ['m6-inequalities','algebra-language']),
 ('rearranging|rearrange the formula|subject of the formula', ['m6-rearrange']),
 ('nth term|nth-term|position-to-term', ['m6-nth-term','m5-sequences']),
 ('simultaneous equation|solving graphically', ['m6-simultaneous']),
 ('quadratic graph|quadratic equation', ['m6-quadratic-graphs']),
 ('bearing|bearings', ['m6-bearings']),
 ('congruent|congruence', ['m6-congruence']),
 ('perpendicular bisector|angle bisector|compass construction', ['m6-constructions']),
 ('loci|locus', ['m6-loci']),
 ('relative frequency|experimental probability', ['m6-relative-frequency']),
]
COMPILED=[(re.compile(r'(?<!\w)(?:'+pattern+r')s?(?!\w)',re.I),ids) for pattern,ids in RULES]


def parse(text):
    sections={};active=None;n=None
    for page,block in enumerate(text.rstrip('\f').split('\f'),1):
        if page<7: continue
        for line in block.splitlines():
            h=HEAD.match(line)
            if h:
                active=None;n=None
                if h[3].lower()=='foundation' and h[1] in '1256':
                    component='Single paper' if h[1] in '12' else {'non-calculator':'Paper 1','calculator':'Paper 2'}.get((h[4] or '').lower())
                    if component is None: raise ValueError('Missing calculator component')
                    active=('M'+h[1],component)
                    if active in sections: raise ValueError('Repeated section')
                    sections[active]={}
                continue
            if active and re.match(r'^\s*Contact details\s*$',line,re.I): active=None;n=None
            if not active: continue
            q=Q.match(line)
            if q:
                n=int(q[1]);line=q[2]
                if n in sections[active]: raise ValueError('Repeated question heading')
                sections[active][n]=(page,[])
            if n: sections[active][n][1].append(line)
    return sections


def tags(text,unit,available):
    text=' '.join(text.lower().split());matched=set()
    for pattern,ids in COMPILED:
        if not pattern.search(text):continue
        for sid in ids:
            origin=sid[:2].upper() if re.match(r'm[256]-',sid) else 'M1'
            key=sid if unit==origin else unit.lower()+'-from-'+origin.lower()+'-'+sid
            if key in available: matched.add(key);break
    return matched


def ingest(db,path):
    data=Path(path).read_bytes();sha=hashlib.sha256(data).hexdigest()
    if not db.execute('SELECT 1 FROM examiner_reports WHERE sha=?',(sha,)).fetchone(): raise ValueError('Report must first be audited')
    text=subprocess.run(['pdftotext','-layout','-enc','UTF-8','-','-'],input=data,capture_output=True,check=True,timeout=45).stdout.decode('utf8')
    sections=parse(text);expected={tuple(x) for x in db.execute("SELECT unit,component FROM examiner_sections WHERE report_sha=? AND status='linked'",(sha,))}
    if set(sections)!=expected: raise ValueError('Report sections differ from audited sections')
    staged=[]
    for (unit,component),qs in sections.items():
        source={r[0]:r[1] for r in db.execute("SELECT num,start_page FROM examiner_anchors WHERE report_sha=? AND unit=? AND component=? AND status='linked'",(sha,unit,component))}
        if {n:v[0] for n,v in qs.items()}!=source: raise ValueError('Question headings/pages differ from audit')
        available={r[0] for r in db.execute('SELECT id FROM skills WHERE unit=?',(unit,))}
        for n,(page,lines) in qs.items():
            for skill in sorted(tags(' '.join(lines),unit,available)):
                staged.append((sha,unit,component,n,skill,'provisional report-derived whole-question topic'))
    with db:
        db.execute('DELETE FROM examiner_skill_evidence WHERE report_sha=?',(sha,))
        db.executemany('INSERT INTO examiner_skill_evidence VALUES(?,?,?,?,?,?)',staged)
    return len(staged)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--out',required=True);p.add_argument('reports',nargs='+');a=p.parse_args()
    if not Path(a.db).is_file():raise FileNotFoundError(a.db)
    with sqlite3.connect(a.db) as db:
        db.execute('PRAGMA foreign_keys=ON');db.executescript(SCHEMA)
        for path in a.reports: print(Path(path).name,ingest(db,path))
        q=db.execute('SELECT * FROM examiner_skill_evidence ORDER BY 1,2,3,4,5')
        with open(a.out,'w',newline='',encoding='utf8') as f:
            w=csv.writer(f);w.writerow(x[0] for x in q.description);w.writerows(q)
if __name__=='__main__':main()
