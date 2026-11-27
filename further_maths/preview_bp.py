"""Source-free AS1 preview boundary. This is not an examination-release API."""
import re
from active_difficulty import Resolver, MODES, require
from readiness_bo import conservative_preview_eligible, conservative_preview_resolve

ITEM_ID = re.compile(r'CAL\.([a-z0-9-]+)\.T([1-6])\.V([1-3])')


class PreviewCatalogue:
    """Both discovery and retrieval use the same conservative BO policy.

    A future authenticated teacher integration should use this boundary, not
    Resolver._resolve or its legacy selection modes. It does not provide
    authentication, persistent storage, production rendering, or release.
    """
    def __init__(self):
        self._resolver = Resolver()

    @staticmethod
    def _mode(mode):
        require(isinstance(mode, str) and mode in MODES, 'Unknown preview mode')

    def list_ids(self, *, mode):
        self._mode(mode)
        return tuple(f'CAL.{path}.T{tier}.V{variant}'
                     for path in sorted(self._resolver.bases)
                     for tier in range(1, 7)
                     if conservative_preview_eligible(self._resolver, path, tier, mode)
                     for variant in (1, 2, 3))

    def get(self, item_id, *, mode):
        self._mode(mode)
        require(isinstance(item_id, str), 'Invalid preview item ID')
        match = ITEM_ID.fullmatch(item_id)
        require(match is not None, 'Invalid preview item ID')
        path, tier, variant = match.groups()
        item = conservative_preview_resolve(self._resolver, path, int(tier), int(variant), mode=mode)
        require(item['teacher_approved'] is False and mode != 'approved_exam', 'Exam release prohibited')
        return {'mode': mode, 'release_allowed': False, 'exam_ready': False, 'item': item}
