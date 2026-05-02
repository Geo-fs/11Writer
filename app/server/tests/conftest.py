from __future__ import annotations

import sys
import warnings
from pathlib import Path

from pydantic.warnings import UnsupportedFieldAttributeWarning


# Keep `src.*` imports stable for direct pytest runs from the repo root or
# `app/server`, even when the editable install state is stale or absent.
SERVER_ROOT = Path(__file__).resolve().parents[1]
server_root_str = str(SERVER_ROOT)
if server_root_str not in sys.path:
    sys.path.insert(0, server_root_str)


# FastAPI currently rebuilds aliased Pydantic fields into temporary TypeAdapters
# during request parsing, which emits noisy warnings even though the schemas are
# valid and the route contracts behave correctly.
warnings.filterwarnings(
    "ignore",
    category=UnsupportedFieldAttributeWarning,
    message=r"The '(alias|validation_alias|serialization_alias)' attribute with value .* was provided to the `Field\(\)` function, which has no effect in the context it was used\..*",
)
warnings.simplefilter("ignore", UnsupportedFieldAttributeWarning)
