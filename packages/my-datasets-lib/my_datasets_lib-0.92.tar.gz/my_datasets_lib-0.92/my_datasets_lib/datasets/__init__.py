'''Makes datasets behave like bundles of submodules.'''

from . import cdc, food_ids, atu_dirty, atu_clean

__all__ = ["cdc", "food_ids", "atu_dirty", "atu_clean"]

