"""Private, fingerprint-bound presentation successor of the BO/BP catalogue.

The caller supplies private edits; no source, payload or review ledger is bundled.
Mathematical facts and rubrics are invariant. This is not certification or release.
"""
import copy
import re
from active_difficulty import Resolver, require
from marking_review import fingerprint
from marking_batch import ITEM_ID
from solution_review_bm import PLAIN_SIGNALS
from readiness_bo import conservative_preview_eligible

REVISION = 'FM-16BQ'
TEXT_FIELDS = ('question_latex', 'final_answer_latex', 'worked_solution_latex')
COMMANDS = set('frac sqrt pi left right operatorname geq ne theta leq mapsto Re pm delta arg alpha beta gamma phi lambda cdot mp mathrm begin end mathbf det times ge le in cos arccos mathbb rho'.split())
ENVIRONMENTS = {'matrix', 'pmatrix', 'vmatrix'}


def safe_parts(text):
    require(isinstance(text, str) and text.strip() and r'\$' not in text, 'Invalid math text')
    parts = text.split('$')
    require(len(parts) % 2 == 1, 'Unbalanced math delimiters')
    for fragment in parts[1::2]:
        require(fragment.strip() and not re.search(r'[%#\r\n~]', fragment), 'Unsafe math fragment')
        stack = []
        for token in re.finditer(r'\\(?:[a-zA-Z]+|.)|&', fragment):
            value = token[0]
            if value in (r'\begin', r'\end'):
                env = re.match(r'\{([a-z]+)\}', fragment[token.end():])
                require(env and env[1] in ENVIRONMENTS, 'Invalid math environment')
                if value == r'\begin':
                    require(not stack, 'Nested environment'); stack.append(env[1])
                else:
                    require(stack and stack.pop() == env[1], 'Unmatched environment')
            elif value in (r'\\', '&'):
                require(stack, 'Matrix alignment outside environment')
            else:
                require(value in (r'\{', r'\}', r'\ ') or value[1:] in COMMANDS, 'Unsupported math command')
        require(not stack, 'Unclosed environment')
        depth = 0
        for char in re.sub(r'\\[{}]', '', fragment):
            depth += (char == '{') - (char == '}')
            require(depth >= 0, 'Unbalanced braces')
        require(depth == 0, 'Unbalanced braces')
        require(not re.search(r'\^(?:[+-]|\d{2,})', fragment), 'Ambiguous unbraced exponent')
    return parts


def canonical(text):
    """Lexical comparison, not an algebraic or pedagogical equivalence oracle."""
    text = text.replace('$', '').replace('plus or minus', '+/-')
    text = re.sub(r'\s+squared\b', '^2', text)
    text = re.sub(r'\s+cubed\b', '^3', text)
    for word, sign in [('minus', '-'), ('plus', '+'), ('times', '*')]:
        text = re.sub(r'\s+' + word + r'\s+', sign, text)
    text = re.sub(r'\\(?:operatorname|mathrm)\{([A-Za-z]+)\}', r'\1', text)
    for word, token in [('theta','theta'),('alpha','alpha'),('beta','beta'),('gamma','gamma'),('phi','phi'),('delta','delta'),('lambda','lambda'),('pi','pi'),('leq','<='),('geq','>='),('pm','+/-'),('mp','-/+'),('cdot','*')]:
        text = re.sub(r'\\' + word + r'(?![A-Za-z])', lambda _: token, text)
    def roots(value):
        match = re.search(r'\\sqrt\{', value)
        if not match:
            return value
        depth, pos = 1, match.end()
        while pos < len(value) and depth:
            depth += (value[pos] == '{') - (value[pos] == '}'); pos += 1
        require(depth == 0, 'Unbalanced radical')
        return value[:match.start()] + 'sqrt(' + roots(value[match.end():pos-1]) + ')' + roots(value[pos:])
    text = roots(text)
    # A starred polynomial is not multiplication; keep the star semantic distinct.
    text = text.replace('Q^{*}', 'QSTAR').replace('Q^*', 'QSTAR')
    return re.sub(r'\s+', '', text)


def equivalent_span(old, new):
    if old == 'min of thresholds < h <= max':
        return new == 'the smaller threshold is strictly below $h$ and $h$ is at most the larger threshold'
    if 'Q*(' in old:
        # Plain predecessor star names the conjugated polynomial, not a product.
        old = old.replace('Q*(', 'QSTAR(')
    return canonical(old) == canonical(new)


def apply_spans(text, spans):
    result, cursor = [], 0
    require(isinstance(spans, list) and spans, 'Missing edits')
    for span in spans:
        start, end, old, new = (span[k] for k in ('start', 'end', 'old', 'new'))
        require(type(start) is int and type(end) is int and cursor <= start < end <= len(text), 'Invalid span bounds')
        require(text[start:end] == old and isinstance(new, str) and equivalent_span(old, new), 'Changed mathematical tokens')
        result.extend((text[cursor:start], new)); cursor = end
    result.append(text[cursor:]); updated = ''.join(result)
    parts = safe_parts(updated)
    require(not any(p.search(' '.join(parts[::2])) for p in PLAIN_SIGNALS.values()), 'Residual notation signal')
    return updated


def fields(payload):
    return {'question': payload['question_latex'], 'answer': payload['final_answer_latex'],
            **{f'step_{i}': s for i, s in enumerate(payload['worked_solution_latex'], 1)}}


def revise(item, record):
    require(item['id'] == record['id'] and item['revision'] == record['predecessor_revision'] and fingerprint(item) == record['predecessor_fingerprint'], 'Wrong predecessor')
    require(item['teacher_approved'] is False, 'Approved predecessor not supported')
    output = copy.deepcopy(item); p = output['payload']; before = fields(p); after = dict(before)
    edits = record['edits']; require(isinstance(edits, dict) and set(edits) <= set(before), 'Unknown field')
    for key, spans in edits.items():
        after[key] = apply_spans(before[key], spans)
    # Defined vocabulary only; do not reveal a solution method for rank tasks.
    definition = record.get('definition')
    if definition == 'symmetric_2x2':
        require(p['path'] in ('matrix-add-subtract', 'matrix-equation') and p['tier'] == 5 and after['question'].count('is symmetric') == 1, 'Unexpected symmetry definition')
        after['question'] = after['question'].replace('is symmetric', 'is symmetric (its two off-diagonal entries are equal)')
    elif definition == 'rank_rows':
        require(p['path'] == 'det-three' and p['tier'] == 5 and after['question'].endswith('its rank is exactly two.'), 'Unexpected rank definition')
        after['question'] += ' Here rank means the maximum number of linearly independent rows.'
    else:
        require(definition is None, 'Unknown definition edit')
    require(before != after, 'Empty successor')
    for text in after.values(): safe_parts(text)
    p.update(question_latex=after['question'], final_answer_latex=after['answer'], worked_solution_latex=[after[f'step_{i}'] for i in range(1, len(p['worked_solution_latex'])+1)])
    require(all(p[k] == item['payload'][k] for k in p if k not in TEXT_FIELDS), 'Non-presentation change')
    output['revision'] = REVISION
    return output


class SuccessorResolver(Resolver):
    """Opt-in version; inherited resolver remains the historical BO baseline."""
    def __init__(self, records):
        super().__init__()
        self.edits = {}
        for record in records:
            match = ITEM_ID.fullmatch(record['id'])
            require(match is not None and record['id'] not in self.edits, 'Duplicate or invalid edit ID')
            path, tier, variant = match.groups()
            item = super()._resolve(path, int(tier), int(variant))
            self.edits[item['id']] = copy.deepcopy(record)
            revise(item, record)

    def _resolve(self, path, tier, variant):
        item = super()._resolve(path, tier, variant)
        record = self.edits.get(item['id'])
        return revise(item, record) if record is not None else item

    def guarded(self, item_id, mode):
        match = ITEM_ID.fullmatch(item_id) if isinstance(item_id, str) else None
        require(match is not None, 'Invalid item ID')
        path, tier, variant = match.groups(); tier, variant = int(tier), int(variant)
        require(isinstance(mode, str) and conservative_preview_eligible(self, path, tier, mode), 'Preview not eligible')
        item = self._resolve(path, tier, variant)
        return {'mode': mode, 'release_allowed': False, 'exam_ready': False, 'item': item}
