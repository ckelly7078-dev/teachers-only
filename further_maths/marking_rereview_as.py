"""Re-review the twelve amended pilot items; frozen new fingerprints, no approvals."""
import json
from marking_pilot_ar import records as prior_records

FINGERPRINTS = {
    'root-sum-product': ('4017da6141464c09fd1fd2dd45c5682668bc4aa6cb892ece968439d6f7399150', '8076fe0a7f42ae5dcc00b3d200d5e1048d8e8437e23751d88819be31e82296d0', '9ea799fb53026ef4d1f021adb9efd421aed3f881cd356f629f194cdfeb1e68ba'),
    'cartesian-product': ('277ea7bd1cae425970b5b8c429122dd754f804eb73a722049c0698daa3feb0e1', '9cbf4ef84999cdb7d3a0eb0024a62a41bda8b6d0e6596adfd30c8fed5789b0ed', '8cc87a9040be15f67df81429b98f6ff2351c055de8b9df4877e95dc7e567e74e'),
    'det-two': ('14bdc825cefc8091a6dee113c74a5ea2d8cf66a728c0dda0bcee8a958f0f12f9', '75e92347dea4b46e7072466a17bed32740e335ee165b12680a8c02b77720ee88', 'bca1ee615b0f7c2df9ee2a78f19fb74234363bb5f5a443d5c58a21ecd065c636'),
    'scalar-product': ('989bb1f3527f6214f93b3373bb47a7d38fd99005f6e935a33e583c98328d90e0', 'fe7a6fc6e4540ab6c00b3472bdb391b3068a0d178d54389385d5b380033355f3', 'ce6ecd940e6818d04ee24ab28275beae303e7048b759ad56cb45236befb893b9'),
}


def records():
    for record in prior_records():
        _, path, _, variant = record['id'].split('.')
        old = record['fingerprint']
        record['fingerprint'] = FINGERPRINTS[path][int(variant[1:]) - 1]
        record['supersedes_fingerprint'] = old
        record['reviewer'] = 'AI editorial re-review FM-16AS (teacher approval pending)'
        checks = record['checks']
        checks['mathematical_correctness']['evidence'] += ' Prompt, facts, worked solution and final answer unchanged in AS.'
        checks['criterion_allocation'] = {'decision': 'pass', 'evidence': 'The amended M1 requires the actual mathematical method, not just coefficient or component identification; A1 requires the entire exact answer. Total two marks unchanged.'}
        checks['alternative_methods']['evidence'] += ' Equivalent method now expressly accepted in the active rubric.'
        checks['consequential_errors']['evidence'] += ' Amended rubric expressly retains method credit for subsequent arithmetic slips, not incorrect methods, and requires exact final accuracy.'
        if path == 'det-two':
            checks['presentation'] = {'decision': 'pass', 'evidence': 'Unrelated squared-parameter warning removed; signed subtraction and absolute-value errors are relevant. Text inspected; no renderer used.'}
        yield record


if __name__ == '__main__':
    for record in records():
        print(json.dumps(record, sort_keys=True))
