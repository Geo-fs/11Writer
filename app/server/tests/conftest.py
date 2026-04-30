from __future__ import annotations

import sys
from pathlib import Path


# Keep `src.*` imports stable for direct pytest runs from the repo root or
# `app/server`, even when the editable install state is stale or absent.
SERVER_ROOT = Path(__file__).resolve().parents[1]
server_root_str = str(SERVER_ROOT)
if server_root_str not in sys.path:
    sys.path.insert(0, server_root_str)
