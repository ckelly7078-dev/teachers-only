"""Validate a batch of version-bound editorial records without modifying the bank."""
import argparse
import collections
import json
import re
from pathlib import Path
from active_difficulty import Resolver, require
from marking_review import validate_review

ITEM_ID = re.compile(r'CAL\.([a-z0-9-]+)\.T([1-6])\.V([1-3])')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def validate_batch(records, resolver=None):
    resolver = Resolver() if resolver is None else resolver
    seen, results = set(), []
    for record in records:
        require(isinstance(record, dict), 'Expected review object')
        item_id = record.get('id')
        match = ITEM_ID.fullmatch(item_id) if isinstance(item_id, str) else None
        require(match is not None, 'Invalid item identifier')
        require(item_id not in seen, 'Duplicate review: ' + item_id)
        path, tier, variant = match.groups()
        resolver._key(path, int(tier), int(variant))
        item = resolver._resolve(path, int(tier), int(variant))
        status = validate_review(item, record)
        for row, criterion in zip(record['allocation'], item['payload']['rubric']):
            if 'type' in criterion and status == 'editorial_review_recorded':
                require(row['marks'][criterion['type']] == criterion['marks'],
                        'Changed existing type requires a revise decision')
        seen.add(item_id)
        results.append({'id': item_id, 'fingerprint': record['fingerprint'], 'status': status})
    require(bool(results), 'Empty review batch')
    return {'records': len(results), 'statuses': dict(collections.Counter(r['status'] for r in results)),
            'teacher_approved': 0, 'results': results}


def read_batch(path):
    with Path(path).open(encoding='utf-8') as stream:
        return [json.loads(line, object_pairs_hook=unique_object) for line in stream if line.strip()]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch', type=Path, help='JSON Lines, one version-bound review per item')
    args = parser.parse_args()
    print(json.dumps(validate_batch(read_batch(args.batch)), indent=2, sort_keys=True))
