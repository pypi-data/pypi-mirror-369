'''Makes datasets behave like bundles of submodules.'''

from . import cdc, food_ids, atu_dirty, atu_clean, timeuse_ids, timeuse_ids_clean

__all__ = ["cdc", "food_ids", "atu_dirty", "atu_clean", "timeuse_ids",
           "timeuse_ids_clean"]

