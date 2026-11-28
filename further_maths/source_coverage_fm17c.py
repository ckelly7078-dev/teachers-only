"""Complete private source-part coverage, with no inferred feature-level marks."""
import copy
import hashlib
import json
from collections import Counter, defaultdict

from active_difficulty import require
from mark_routes_fm17b import bind_routes, part_routes
from source_evidence_fm17 import part_signature


def route_signature(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


class SourceCoverage:
    """Source evidence for the existing private engine; never a marking decision.

    Detailed routes and unresolved printed allocations must partition the usable
    parts. A stage component is not a separate examination demand or extra mark.
    """
    def __init__(self, bank, routes, ambiguous, components=(), conditions=()):
        self.bank = bank
        self._routes = bind_routes(bank, routes)
        self._ambiguous = {}
        self._components = defaultdict(list)
        self._conditions = defaultdict(list)
        for row in ambiguous:
            key = self._key(row)
            part = self._part(row, key)
            require(key not in self._routes and key not in self._ambiguous, 'Repeated source disposition')
            require(row['scheme_sha256'] == bank.sources[part['scheme_source']]['sha256']
                    and row['scheme_page'] == part['scheme_page'] and type(row['scheme_page']) is int,
                    'Wrong scheme locator')
            require(row['printed_allocation'] == part['printed_allocation'], 'Printed allocation changed')
            require(all(isinstance(row[k], str) and row[k].strip() for k in ('geometry', 'reason')),
                    'Missing ambiguity explanation')
            require(set(row) == {'series','number','ordinal','part_signature','scheme_sha256','scheme_page',
                                  'printed_allocation','geometry','reason','automatic_award'}, 'Invalid ambiguity fields')
            self._ambiguous[key] = copy.deepcopy(row)
        require(set(self._routes) | set(self._ambiguous) == set(bank.parts), 'Incomplete source coverage')
        seen = set()
        for row in components:
            key = self._key(row); self._part(row, key)
            skill = row['skill']; stage_ids = row['stage_ids']; rid = row['route_id']
            require(key in self._routes and skill in bank.skills and key in bank.links[bank.skills[skill]['concept_id']],
                    'Component exceeds source parent link')
            record = self._routes[key]
            require(row['route_signature'] == route_signature(record), 'Stale route component')
            route = next((r for r in record['routes'] if r['id'] == rid), None)
            require(route is not None and isinstance(stage_ids,list) and stage_ids and len(set(stage_ids)) == len(stage_ids)
                    and set(stage_ids) <= {s['id'] for s in route['stages']}, 'Invalid stage references')
            require(row['basis'] == 'editorial_component_of_printed_route' and row['standalone_skill_assessment'] is False
                    and row['separate_marks'] is False and isinstance(row['note'],str) and row['note'].strip(),
                    'Invalid component basis')
            identity = (skill,key,rid,tuple(stage_ids)); require(identity not in seen, 'Repeated component'); seen.add(identity)
            self._components[skill].append(copy.deepcopy(row))
        seen = set()
        for row in conditions:
            key = self._key(row); part = self._part(row,key)
            require(row['paper_sha256'] == bank.sources[part['paper_source']]['sha256']
                    and row['paper_page'] == part['paper_page'] and type(row['paper_page']) is int,
                    'Wrong paper locator')
            require(row['kind'] in ('method_restriction','interpretation_caveat') and isinstance(row['note'],str)
                    and row['note'].strip(), 'Invalid source condition')
            ident=(key,row['kind']); require(ident not in seen, 'Repeated source condition'); seen.add(ident)
            self._conditions[key].append(copy.deepcopy(row))

    @staticmethod
    def _key(row):
        return row['series'],row['number'],row['ordinal']

    def _part(self,row,key):
        require(key in self.bank.parts and row['part_signature'] == part_signature(self.bank,key), 'Unknown or stale source part')
        require(row['automatic_award'] is False, 'Automatic award prohibited')
        return self.bank.parts[key]

    def part(self,key):
        require(key in self.bank.parts, 'Unknown or disputed source part')
        if key in self._ambiguous:
            row=self._ambiguous[key]; self._part(row,key)
            result={'status':'printed_allocation_ambiguous','automatic_award':False,'routes':[],
                    'ambiguity':copy.deepcopy(row)}
        else:
            result=part_routes(self.bank,self._routes,key)
        for row in self._conditions.get(key,[]): self._part(row,key)
        result['source_conditions']=copy.deepcopy(self._conditions.get(key,[]))
        return result

    def skill_components(self,skill):
        require(skill in self.bank.skills,'Unknown skill')
        rows=self._components.get(skill,[])
        for row in rows:
            key=self._key(row); self._part(row,key)
            require(row['route_signature']==route_signature(self._routes[key]),'Stale route component')
        return copy.deepcopy(rows)

    def summary(self):
        counts=Counter(key[0] for key in self._routes)
        return {'usable_parts':len(self.bank.parts),'detailed_routes':len(self._routes),
                'ambiguous_allocations':len(self._ambiguous),'detailed_marks':sum(self.bank.parts[k]['marks'] for k in self._routes),
                'ambiguous_marks':sum(self.bank.parts[k]['marks'] for k in self._ambiguous),
                'detailed_parts_by_series':dict(counts),'component_links':sum(map(len,self._components.values())),
                'component_skills':len(self._components),'source_conditions':sum(map(len,self._conditions.values())),
                'automatic_award':False,'exam_ready':False}
