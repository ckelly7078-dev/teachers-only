"""Specification-linked skill groups and conservative candidate classification.

Only editorial labels, source pages and inferred skill IDs persist. No verbatim
paper text. Never promote questions or change existing teacher/source reviews.
"""
import argparse, csv, json, re, sqlite3, zipfile
from pathlib import Path
from collections import defaultdict, Counter
from .expand import pages, HEAD, PART, ROMAN, refresh_summary

# unit|strand|printed page|slug|editorial label|distinctive matching phrases
ADDITIONS = '''M2|N|17|index-laws|Positive integer index laws|index law;index notation;write as a single power
M2|N|17|factors|HCF, LCM and prime factorisation|highest common factor;lowest common multiple;least common multiple;prime factor;hcf;lcm
M2|N|17|decimal-operations|Decimal arithmetic|multiply decimals;divide decimals
M2|N|17|significant-figures|Significant figures|significant figure
M2|N|17|recurring-decimals|Recurring decimals and fractions|recurring decimal;recurring
M2|N|17|mixed-fractions|Fraction arithmetic including mixed numbers|mixed number;improper fraction
M2|N|17|repeated-change|Repeated percentage change|compound interest;each year;repeated percentage
M2|N|17|finance|Financial applications|mortgage;insurance;taxation;income tax;investment
M2|N|17|expand|Expand single brackets|expand the bracket;expand and simplify;expand
M2|N|17|factorise|Extract common factors|factorise;factorize
M2|N|18|equations|Linear equations including unknowns on both sides|solve the equation;solve for x
M2|N|18|midpoint-length|Midpoints and coordinate distances|midpoint;length of the line segment
M2|N|18|gradient|Linear graph gradients and intercepts|gradient;intercept
M2|G|18|density|Density and compound measures|density;mass per unit volume
M2|G|18|plane-area|Perimeter and area of quadrilaterals|area of the trapezium;area of the parallelogram;area of the kite;area of the rhombus
M2|G|18|composite-area|Composite perimeter and area|compound shape;composite shape
M2|G|18|prism-volume|Volume of right prisms|volume of the prism;volume of this prism;cross section
M2|G|18|pythagoras|Pythagoras in two dimensions|pythagoras;hypotenuse
M2|H|19|venn-three|Three-set Venn diagrams|three circle venn;three-circle venn
M2|H|19|grouped-statistics|Grouped mean, median and modal class|modal class;median class;estimate the mean;grouped frequency
M2|H|19|scatter|Scatter plots, trends and causality|line of best fit;outlier;extrapolate;interpolate;correlation does not imply;scatter diagram;correlation
M5|N|14|mental-arithmetic|Non-calculator arithmetic|without a calculator;show your calculation
M5|N|14|estimation|Approximation and estimation|estimate the answer;approximate answer;estimate the calculation
M5|N|14|ratio|Ratios and sharing|simplest ratio;in the ratio;share in the ratio;ratio in its simplest form
M5|N|14|proportion|Proportion, scaling and exchange|best buy;best value;exchange rate;recipe;direct proportion
M5|N|14|sequences|Number patterns and sequences|term-to-term;position-to-term;next term;sequence;triangular number
M5|N|14|travel-graphs|Real-context graphs|distance-time;distance/time;conversion graph;travel graph
M5|G|15|measurement|Reading measurement scales|reading on the scale;measuring instrument
M5|G|15|imperial|Imperial and metric equivalents|imperial;inches;pounds and ounces;gallons
M5|G|15|scale|Maps and scale drawings|scale drawing;map scale;scale of the map
M5|G|15|polygon-angles|Triangle and polygon angle sums|sum of the angles;angle sum;angles in a triangle
M5|G|15|transformations|Single plane transformations|reflect;reflection;rotate;rotation;translate;translation;enlarge;enlargement;single transformation
M5|G|15|drawing|Ruler and protractor drawings|draw the triangle;construct the triangle;use a protractor
M5|H|16|probability|Probability language and simple events|probability scale;equally likely;probability;impossible;certain
M5|H|16|outcomes|Systematic outcome listing|list all possible outcomes;list all the possible;systematic list;sample space
M5|H|16|complement|Complementary and mutually exclusive events|mutually exclusive;probability that it does not;probability that it will not
M5|H|16|expectation|Expected frequencies|how many would you expect;expected frequency;expect to get
M6|N|20|binary|Binary and decimal number systems|binary;base 2;base two
M6|N|20|algebra-indices|Algebraic positive index laws|index law;index notation;write as a single power
M6|N|20|trial-improvement|Trial and improvement|trial and improvement
M6|N|20|inequalities|Linear inequalities and number lines|solve the inequality;solve the inequalities;solution set;represent on a number line
M6|N|20|rearrange|Change the subject of formulae|make x the subject;the subject of the formula;change the subject;rearrange the formula
M6|N|20|nth-term|Linear nth terms|nth term;nth-term;position to term rule
M6|N|20|simultaneous|Graphical simultaneous equations|simultaneous equations;solve graphically
M6|N|20|quadratic-graphs|Quadratic graphs and intersections|quadratic graph;quadratic function;curve intersects
M6|G|21|bearings|Bearings|bearing;three-figure bearing
M6|G|21|polygon-angles|Interior and exterior polygon angles|interior angle;exterior angle
M6|G|21|transforms|Transformations and invariants|reflect;reflection;rotate;rotation;translate;translation;vector;single transformation
M6|G|21|enlargement|Enlargement effects on perimeter and area|enlarge;enlargement;scale factor
M6|G|21|congruence|Congruence|congruent;congruence
M6|G|21|constructions|Ruler and compass constructions|perpendicular bisector;angle bisector;compass;compasses
M6|G|21|loci|Loci|locus;loci
M6|H|21|outcomes|Systematic outcome listing|list all possible outcomes;list all the possible;sample space
M6|H|21|relative-frequency|Relative frequency and experimental probability|relative frequency;experimental probability;theoretical probability;sample size
'''
STRANDS={'N':'Number and algebra','G':'Geometry and measures','H':'Handling data'}
PREREQUISITES={'M1':(), 'M2':('M1',), 'M5':('M1',), 'M6':('M1','M2','M5')}
# Existing M1 IDs, with intentionally specific phrases rather than general words.
M1_PHRASES={'number-properties':'prime number;cube number;square number;multiple of;factor of', 'rounding':'decimal place;nearest whole;round to;correct to the nearest', 'fractions':'simplest form;equivalent fraction;fraction of', 'percentage':'percentage;percent;%','finance':'wages;salary;profit;loss;discount;simple interest','formula':'substitute;use the formula','equations':'solve the equation;solve for x','coordinates':'coordinates;co-ordinates','angles':'vertically opposite;alternate angle;corresponding angle','circles':'circumference;radius;diameter','solids':'net of;faces and edges;plan and elevation','metric':'millimetres;centimetres;kilograms;millilitres;convert to metres','rates':'average speed;miles per gallon;kilometres per hour','area':'perimeter;area of;volume of','survey':'random sample;biased question','organise-data':'two-way table;venn diagram','averages':'mean;median;mode;range','charts':'pie chart;bar chart;pictogram;frequency diagram','correlation':'scatter diagram;correlation'}


def build(db):
    base=defaultdict(list)
    for r in db.execute("SELECT * FROM skills WHERE unit='M1'"):
        base['M1'].append((r['id'],r['strand'],r['label'],r['page'],r['terms'],M1_PHRASES.get(r['id'],'')))
    for line in ADDITIONS.strip().splitlines():
        u,s,p,slug,label,terms=line.split('|')
        base[u].append((u.lower()+'-'+slug,STRANDS[s],label,int(p),terms.replace(';',' '),terms))
    result=defaultdict(list)
    for unit,parents in PREREQUISITES.items():
        for origin in (unit,)+parents:
            for sid,strand,label,page,terms,phrases in base[origin]:
                key=sid if origin==unit else unit.lower()+'-from-'+origin.lower()+'-'+sid
                if origin==unit=='M1': pass
                else: db.execute('INSERT OR IGNORE INTO skills VALUES(?,?,?,?,?,?)',(key,unit,strand,label,page,terms))
                result[unit].append((key,origin,label,phrases,page))
    return result


def split_text(blocks):
    records=defaultdict(lambda: {'page':None,'text':[]}); n=0; letter=part=''
    for page,block in enumerate(blocks,1):
        if page<2: continue
        for line in block.splitlines():
            m=HEAD.match(line); text=line.strip()
            if m and int(m[1])==n+1: n+=1; text=(m[2] or '').lstrip(); letter=part=''
            elif not n: continue
            s=PART.match(text)
            if s: letter=part=s[1]; text=text[s.end():]
            r=ROMAN.match(text.strip())
            if r and letter: part=letter+'.'+r[1]
            key=(n,part); rec=records[key]
            if rec['page'] is None: rec['page']=page
            rec['text'].append(text)
    return records


def match_skill(text, groups, unit):
    text=' '.join(text.lower().split()); matches=[]
    for key,origin,label,phrases,page in groups:
        hit=[p for p in phrases.split(';') if p and re.search(r'(?<!\w)'+re.escape(p)+r'(?!\w)',text)]
        if hit: matches.append((max(map(len,hit)),origin==unit,key))
    if not matches: return None
    # Longer explicit phrase wins; equally specific unit-native skill beats inherited.
    matches.sort(reverse=True)
    if len(matches)>1 and matches[0][:2]==matches[1][:2]: return None
    return matches[0][2]


def classify(db,z,groups):
    result=[]
    for pair in db.execute("SELECT * FROM pairs WHERE status='paired' ORDER BY unit,year,series,component").fetchall():
        paper=pair['paper']; unit=pair['unit']; changes=0
        data=split_text(pages(db,z,paper))
        for q in db.execute("SELECT * FROM questions WHERE paper=? AND status='review' AND verified_by IS NULL AND skill IS NULL AND marks>0",(paper,)).fetchall():
            rec=data.get((q['num'],q['part']))
            if not rec or not q['scheme_page'] or rec['page']!=q['page']: continue
            skill=match_skill(' '.join(rec['text']),groups[unit],unit)
            if skill:
                db.execute('UPDATE questions SET skill=? WHERE id=? AND status=\'review\' AND verified_by IS NULL AND skill IS NULL',(skill,q['id'])); changes+=1
        result.append(dict(unit=unit,year=pair['year'],series=pair['series'],component=pair['component'],new_suggestions=changes))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--archive',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    if not Path(a.db).is_file(): raise FileNotFoundError(a.db)
    db=sqlite3.connect(a.db);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
    try:
        with db,zipfile.ZipFile(a.archive) as z:
            groups=build(db); results=classify(db,z,groups); refresh_summary(db)
            for unit in groups: db.execute('INSERT INTO runs(unit,phase,detail) VALUES(?,?,?)',(unit,'taxonomy-v1',json.dumps({'groups':len(groups[unit]),'new_suggestions':sum(r['new_suggestions'] for r in results if r['unit']==unit)})))
        out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
        for name,items in [('classification.csv',results),('taxonomy.csv',[dict(unit=u,id=k,origin=o,label=l,printed_page=p) for u,g in groups.items() for k,o,l,t,p in g])]:
            with (out/name).open('w',newline='',encoding='utf8') as f:
                w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
        print(json.dumps(json.loads(db.execute('SELECT summary FROM state').fetchone()[0]),indent=2))
    finally: db.close()

if __name__=='__main__': main()
