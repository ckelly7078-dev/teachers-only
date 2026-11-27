"""Reference-only matrix solution audit. No question payload changes or approvals."""
import collections
import json
import re
from pathlib import Path
import argparse
from active_difficulty import Resolver, require
from marking_review import fingerprint, inventory_entry
from solution_review_bm import escape_text, PLAIN_SIGNALS, log_flags

PATHS = ('basis-images', 'describe-transform', 'figure-images', 'identity-operations',
         'matrix-add-subtract', 'matrix-conformability', 'matrix-products', 'scalar-matrix', 'zero-matrix')
COMMANDS = frozenset(('left', 'right', 'begin', 'end', 'frac', 'sqrt', 'times'))
ENVIRONMENTS = frozenset(('matrix', 'pmatrix'))


def split_math(text):
    require(isinstance(text, str) and text.strip() and r'\$' not in text, 'Invalid text')
    parts = text.split('$')
    require(len(parts) % 2 == 1, 'Unbalanced math')
    for frag in parts[1::2]:
        require(frag.strip() and not re.search(r'[%#\r\n~]', frag), 'Unsafe fragment')
        stack = []
        tokens = re.finditer(r'\\(?:[a-zA-Z]+|\\| )|[&\\]', frag)
        for match in tokens:
            tok = match.group()
            if tok in (r'\begin', r'\end'):
                env = re.match(r'\{([a-z]+)\}', frag[match.end():])
                require(env and env.group(1) in ENVIRONMENTS, 'Unknown environment')
                if tok == r'\begin':
                    require(not stack, 'Nested matrix')
                    stack.append(env.group(1))
                else:
                    require(stack and stack.pop() == env.group(1), 'Mismatched matrix')
            elif tok in ('&', r'\\'):
                require(bool(stack), 'Matrix alignment outside environment')
            else:
                require(tok == r'\ ' or tok[1:] in COMMANDS, 'Unknown command')
        require(not stack, 'Unclosed matrix')
        depth = 0
        for c in frag:
            if c == '{': depth += 1
            if c == '}': depth -= 1
            require(depth >= 0, 'Unbalanced braces')
        require(depth == 0, 'Unbalanced braces')
    return parts


def tex_text(text):
    return ''.join(escape_text(s) if i % 2 == 0 else '$' + s + '$'
                   for i, s in enumerate(split_math(text)))


def items_for(r):
    for path in PATHS:
        require(r.bases[path][0].startswith('MAT.'), 'Not a matrix pathway')
        for tier in range(1, 7):
            for variant in (1, 2, 3):
                yield r._resolve(path, tier, variant)


def proof(items):
    lines = [r'\documentclass[11pt,a4paper]{article}', r'\usepackage[T1]{fontenc}',
             r'\usepackage{amsmath,amssymb,lmodern}', r'\usepackage[margin=20mm]{geometry}',
             r'\setlength{\parindent}{0pt}', r'\setlength{\parskip}{6pt}', r'\raggedright',
             r'\setlength{\emergencystretch}{3em}', r'\begin{document}']
    records = []
    for page, item in enumerate(items, 1):
        p = item['payload']; steps = p['worked_solution_latex']
        require(inventory_entry(item)['status'] == 'typed_provisional', 'Untyped marking')
        fields = {'question': p['question_latex'], 'answer': p['final_answer_latex']}
        fields.update({f'step_{i}': s for i, s in enumerate(steps, 1)})
        signals = {}
        for key, text in fields.items():
            plain = ' '.join(split_math(text)[::2])
            found = [name for name, pattern in PLAIN_SIGNALS.items() if pattern.search(plain)]
            if found: signals[key] = found
        records.append({'id': item['id'], 'revision': item['revision'], 'fingerprint': fingerprint(item),
                        'skill': p['focus_skill'], 'scope': item['scope'], 'marks': item['marks'],
                        'expected_page': page, 'worked_steps': len(steps), 'oracle_checked': True,
                        'math_delimiters_checked': True, 'plain_notation_signals': signals,
                        'individual_solution_certified': False, 'visual_certified': False,
                        'teacher_approved': False, 'exam_ready': False})
        lines += [r'\typeout{FMITEM:' + item['id'] + '}',
                  r'{\small AS1 matrix solution proof \quad ' + escape_text(item['id']) + r' \quad ' + escape_text(item['revision']) + '}',
                  r'\hrule', r'\textbf{Question} \hfill ' + str(item['marks']) + ' provisional marks',
                  tex_text(fields['question']), r'\textbf{Final answer}', tex_text(fields['answer']),
                  r'\textbf{Worked solution}']
        lines.extend(str(i) + '. ' + tex_text(step) for i, step in enumerate(steps, 1))
        lines += [r'\vfill', r'{\footnotesize Original item. Editorial proof only; not approved for examination use.}', r'\clearpage']
    lines.append(r'\end{document}')
    require(len(records) == len(PATHS)*18 and len({r['id'] for r in records}) == len(records), 'Coverage mismatch')
    return '\n\n'.join(lines) + '\n', records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    tex, records = proof(items_for(Resolver()))
    (args.out/'matrix-proof.tex').write_text(tex, encoding='utf-8')
    (args.out/'matrix-screen.jsonl').write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in records), encoding='utf-8')
    print(json.dumps({'items':len(records), 'plain_notation_items':sum(bool(r['plain_notation_signals']) for r in records)}))
