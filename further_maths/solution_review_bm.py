"""Read-only per-item solution and typesetting screen; never a correctness certificate.

Build a LaTeX proof for each original question, answer and worked solution.
The proof deliberately preserves plain-text notation, rather than silently
normalising it. This is a reference renderer, not the platform renderer.
"""
import argparse
import collections
import json
import re
from pathlib import Path

from active_difficulty import Resolver, require
from marking_review import fingerprint, inventory_entry

TEXT_ESCAPE = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}',
               '#': r'\#', '%': r'\%', '&': r'\&', '_': r'\_',
               '^': r'\textasciicircum{}', '~': r'\textasciitilde{}',
               '<': r'\textless{}', '>': r'\textgreater{}',
               '|': r'\textbar{}'}
PLAIN_SIGNALS = {
    'plain_power': re.compile(r'\^'),
    'plain_inequality_or_plus_minus': re.compile(r'<=|>=|\+/-'),
    'plain_named_math_symbol': re.compile(r'\b(?:theta|pi|sqrt)\b'),
    'plain_function_notation': re.compile(r'\b(?:Re|Im|arg|cos|sin)\('),
}
# Reject unexpected control sequences rather than executing arbitrary TeX.
ALLOWED_MATH_COMMANDS = frozenset('frac sqrt pi left right operatorname geq ne theta leq mapsto Re pm'.split())


def split_math(text):
    require(isinstance(text, str) and text.strip(), 'Missing content')
    require('\\$' not in text, 'Escaped dollars require manual handling')
    parts = text.split('$')
    require(len(parts) % 2 == 1, 'Unbalanced math delimiters')
    for part in parts[1::2]:
        require(part.strip() and set(re.findall(r'\\([a-zA-Z]+)', part)) <= ALLOWED_MATH_COMMANDS,
                'Unexpected or empty math fragment')
        require(not re.search(r'\\[^a-zA-Z ]|[%#&]|[\r\n]', part), 'Unsupported math escape or special character')
    return parts


def escape_text(text):
    return ''.join(TEXT_ESCAPE.get(c, c) for c in text)


def tex_text(text):
    parts = split_math(text)
    return ''.join(escape_text(s) if i % 2 == 0 else '$' + s + '$' for i, s in enumerate(parts))


def screen(item):
    p = item['payload']
    steps = p['worked_solution_latex']
    require(isinstance(steps, list) and steps, 'Missing worked solution')
    require(inventory_entry(item)['status'] == 'typed_provisional', 'Missing provisional rubric')
    fields = {'question': p['question_latex'], 'answer': p['final_answer_latex']}
    fields.update({f'step_{i}': s for i, s in enumerate(steps, 1)})
    signals = {}
    for name, text in fields.items():
        parts = split_math(text)
        plain = ' '.join(parts[::2])
        matches = [key for key, pattern in PLAIN_SIGNALS.items() if pattern.search(plain)]
        if matches:
            signals[name] = matches
    return {'id': item['id'], 'revision': item['revision'], 'fingerprint': fingerprint(item),
            'skill': p['focus_skill'], 'scope': item['scope'], 'marks': item['marks'],
            'worked_steps': len(steps), 'plain_notation_signals': signals,
            'oracle_checked': True, 'math_delimiters_checked': True,
            'individual_solution_certified': False, 'visual_certified': False,
            'teacher_approved': False, 'exam_ready': False}


def reference_diagram(item):
    """Return a generated reference sketch for explicit Argand sketch requests.

    These are review-proof illustrations, not a modification to the active
    question payload or evidence that the production UI renders diagrams.
    """
    p = item['payload']
    path, tier, variant = p['path'], p['tier'], p['variant']
    if path == 'argand-coordinates' and tier in (3, 4, 5, 6):
        f = p['facts']
        if tier == 3:
            x, y = map(int, f[:2])
            require(x < 0 < y and f[2] == '2', 'Unexpected quadrant')
            points = [(x, y, 'P', 'above left')]
        elif tier == 4:
            x, y, u, v, a, b = map(int, f)
            require((u, v, a, b) == (-x, -y, -x, y) and x > 0 and y > 0, 'Unexpected reflections')
            points = [(x, -y, 'P', 'below right'), (x, y, 'R', 'above right'),
                      (u, v, 'I', 'below left'), (a, b, 'B', 'above left')]
        elif tier == 5:
            bx, by = map(int, f[:2]); ax, ay, m = variant + 1, variant + 3, -(variant + 2)
            require((bx, by) == (2*m-ax, -ay) and f[2] == '3', 'Midpoint facts mismatch')
            points = [(ax, ay, 'A', 'above right'), (bx, by, 'B', 'below left'), (m, 0, 'M', 'above left')]
        else:
            a, b = map(int, f[:2]); d = b-a
            require(d > 0, 'Unexpected intercept order')
            points = [(0, -d, '', 'above left'), (d, 0, '', 'below right')]
        extent = max(5, max(max(abs(x), abs(y)) for x, y, _, _ in points)+2)
        scale = 2.15 / extent  # identical scale for the real and imaginary axes
        lines = [rf'\begin{{tikzpicture}}[x={scale:.6f}cm,y={scale:.6f}cm,>=stealth, every node/.style={{font=\small}}]',
                 rf'\draw[->] (-{extent},0)--({extent},0) node[right] {{$\Re z$}};',
                 rf'\draw[->] (0,-{extent})--(0,{extent}) node[above] {{$\mathrm{{Im}} z$}};',
                 r'\node[below left] at (0,0) {$0$};']
        if tier == 5:
            lines.append(rf'\draw[gray] ({ax},{ay})--({bx},{by});')
        if tier == 6:
            lines.append(rf'\draw[<->,blue!65!black,thick] ({-extent+d},-{extent})--({extent},{extent-d});')
        for x, y, name, anchor in points:
            lines += [rf'\fill[blue!65!black] ({x},{y}) circle[radius=1.6pt];',
                      rf'\node[{anchor}] at ({x},{y}) {{{name}$({x},{y})$}};']
        if tier == 4:
            lines.append(r'\node[below] at (0,-' + str(extent+1) + r') {R: real-axis reflection; I: imaginary-axis reflection; B: both.};')
        lines.append(r'\end{tikzpicture}')
        return 'argand_points_or_line', '\n'.join(lines)
    if path == 'complex-regions' and tier == 3:
        a, b = map(int, p['facts']); require(a > 0 and b > 0, 'Unexpected region bounds')
        xmin, xmax, ymin, ymax = -2, a+4, -2, b+2
        scale = 4.1 / (ymax-ymin)
        lines = [rf'\begin{{tikzpicture}}[x={scale:.6f}cm,y={scale:.6f}cm,>=stealth,every node/.style={{font=\small}}]',
                 rf'\fill[blue!12] ({a},{ymin}) rectangle ({xmax},{b});',
                 rf'\draw[->] ({xmin},0)--({xmax},0) node[right] {{$u$}};',
                 rf'\draw[->] (0,{ymin})--(0,{ymax}) node[above] {{$v$}};',
                 r'\node[below left] at (0,0) {$0$};',
                 rf'\draw[thick,blue!65!black] ({a},{ymin})--({a},{b});',
                 rf'\draw[dashed,thick,blue!65!black] ({a},{b})--({xmax},{b});',
                 rf'\draw[draw=blue!65!black,thick,fill=white] ({a},{b}) circle[radius=2.7pt] node[above right] {{$({a},{b})$}};',
                 rf'\node[below right] at ({a},0) {{$u={a}$}};',
                 rf'\node[left] at (0,{b}) {{$v={b}$}};',
                 r'\end{tikzpicture}',
                 r'\par{\small Shading extends indefinitely right and down; dashed edge and open corner are excluded.}']
        return 'argand_half_plane_intersection', '\n'.join(lines)
    return None, None


def proof(items):
    # One item per page, allowing a spill if content exceeds the page height.
    # The log and PDF page audit detect such spills; no clipping box is used.
    lines = [r'\documentclass[11pt,a4paper]{article}',
             r'\usepackage[T1]{fontenc}', r'\usepackage{amsmath,amssymb}',
             r'\usepackage[margin=20mm]{geometry}', r'\usepackage{lmodern,tikz}',
             r'\setlength{\parindent}{0pt}', r'\setlength{\parskip}{6pt}', r'\raggedright', r'\setlength{\emergencystretch}{3em}',
             r'\begin{document}']
    records = []
    for page, item in enumerate(items, 1):
        rec = screen(item)
        rec['expected_page'] = page
        kind, diagram = reference_diagram(item)
        rec['reference_diagram'] = kind
        records.append(rec)
        p = item['payload']
        lines += [r'\typeout{FMITEM:' + item['id'] + '}',
                  r'{\small AS1 solution proof \quad ' + escape_text(item['id']) + r' \quad ' + escape_text(item['revision']) + '}',
                  r'\hrule', r'\textbf{Question} \hfill ' + str(item['marks']) + ' provisional marks',
                  tex_text(p['question_latex']), r'\textbf{Final answer}', tex_text(p['final_answer_latex']),
                  r'\textbf{Worked solution}']
        lines.extend(str(i) + '. ' + tex_text(step) for i, step in enumerate(p['worked_solution_latex'], 1))
        if diagram:
            lines += [r'\textbf{Reference sketch (generated from question facts)}', diagram]
        lines += [r'\vfill', r'{\footnotesize Original item. Editorial proof only; not approved for examination use.}', r'\clearpage']
    lines.append(r'\end{document}')
    return '\n\n'.join(lines) + '\n', records


def items_for(topic, resolver=None):
    r = Resolver() if resolver is None else resolver
    require(topic == 'algebra_complex', 'This reference renderer currently supports algebra and complex numbers only')
    prefixes = ('ALG.', 'CPX.')
    for path, (skill, _, _) in sorted(r.bases.items()):
        if skill.startswith(prefixes):
            for tier in range(1, 7):
                for variant in (1, 2, 3):
                    yield r._resolve(path, tier, variant)


def log_flags(log):
    """Bind TeX diagnostic lines to the active item marker; retain all warnings."""
    current = None
    seen = []
    flags = collections.defaultdict(list)
    for line in log.splitlines():
        marker = re.fullmatch(r'FMITEM:(CAL\.[a-z0-9-]+\.T[1-6]\.V[1-3])', line.strip())
        if marker:
            current = marker.group(1)
            require(current not in seen, 'Duplicate TeX item marker')
            seen.append(current)
        elif re.search(r'Overfull \\[hv]box|Missing character:|^!|^LaTeX (?:Font )?Warning:', line):
            flags[current or 'global'].append(line.strip())
    return seen, dict(flags)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topic', choices=('algebra_complex',), default='algebra_complex')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    tex, records = proof(items_for(args.topic))
    require(len(records) == 828, 'Unexpected batch coverage')
    require(len({rec['id'] for rec in records}) == len(records), 'Duplicate item')
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'solution-proof.tex').write_text(tex, encoding='utf-8')
    (args.out / 'solution-screen.jsonl').write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in records), encoding='utf-8')
    print(json.dumps({'items': len(records), 'plain_notation_items': sum(bool(r['plain_notation_signals']) for r in records),
                      'individual_solution_certified': 0, 'visual_certified': 0, 'teacher_approved': 0}, indent=2))


if __name__ == '__main__':
    main()
