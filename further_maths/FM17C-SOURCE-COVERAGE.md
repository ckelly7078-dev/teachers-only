# FM-17C: complete private source coverage

Continue FM-17B knowledge-base development. No separate teacher interface, canonical question change, scope promotion, empirical calibration or automatic award is introduced.

## Private engine contract

Load `KnowledgeBank` as before, then use the private FM-17C evidence registers:

```python
from marking_batch import read_batch
from source_coverage_fm17c import SourceCoverage

coverage = SourceCoverage(
    bank,
    read_batch(root / 'FM17C-source-mark-routes.jsonl'),
    read_batch(root / 'FM17C-ambiguous-allocations.jsonl'),
    read_batch(root / 'FM17C-route-component-links.jsonl'),
    read_batch(root / 'FM17C-source-conditions.jsonl'),
)
result = coverage.part(source_part_key)
components = coverage.skill_components(skill_id)
```

The two disposition registers partition all usable source parts. Detailed routes preserve the checked primary allocation, alternative totals and stage dependencies. Ambiguous printed allocations retain the source geometry and exact codes but deliberately return no feature-level award route. Disputed parts remain outside the usable source index. Source conditions distinguish task restrictions and interpretation caveats from printed marking exceptions. All records are private, version-bound evidence, not grading decisions. Component links are neither standalone assessed skills nor additional marks. An absence of a component link is not proof of syllabus exclusion.

The private checkpoint accounts for 166 usable parts (163 detailed, three ambiguous) across eight source sets. It retains 24 previously interpreted parts and adds 139 detailed parts. Combined note-level and component-level evidence covers 100 of 117 skills; 17 remain without specific evidence in the investigated parent parts. The 2021 detailed breakdown provides explicit caps, follow-through and partial-credit notes; other worked schemes must not be assumed to specify equivalent rules. The three invariant-line replacement candidates remain noncanonical until migration and fresh proof/evidence generation. No database changes. The original-item marking context and eligibility guards remain unchanged.

Run `python -m unittest discover -s further_maths -p 'test_*.py'` from the repository root. The private QA report distinguishes structural route verification, source-page review and targeted independent mathematical checks; these are not fresh derivations of every source solution. Existing Teachers Only generator and marking-engine live integration, teacher approval and empirical difficulty evidence remain separate. Keep all private sources, databases, item-level evidence and credentials out of Git. No merge or deployment.
