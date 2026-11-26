"""Source-free structural and exact-fact check; not teacher approval."""
import importlib
from pathlib import Path
from skill_detail import detail_map

def main():
    skills = {f'{concept}.{key}' for concept, entries in detail_map().items() for key, _ in entries}
    seen = set()
    total = 0
    for path in sorted(Path(__file__).parent.glob('calibration*bank.py')):
        bank = importlib.import_module(path.stem)
        oracle = importlib.import_module(path.stem.replace('_bank', '_oracle'))
        for key, skill in bank.PATHS.items():
            assert skill in skills and skill not in seen, (key, skill)
            seen.add(skill)
            for level in range(1, 7):
                for variant in (1, 2, 3):
                    item = bank.make(key, level, variant)
                    assert item['focus_skill'] == skill, (key, level, variant)
                    assert oracle.check(item), (key, level, variant)
                    total += 1
        print(path.stem, total, flush=True)
    assert seen == skills and len(seen) == 117 and total == 2106
    print(f'PASS: {len(seen)} skills, {total} structured exact-fact checks')

if __name__ == '__main__':
    main()
