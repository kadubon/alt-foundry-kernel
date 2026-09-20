"""Keep Hypothesis' machine-specific cache outside the publication tree."""

import os
import tempfile
from pathlib import Path

os.environ.setdefault(
    "HYPOTHESIS_STORAGE_DIRECTORY", str(Path(tempfile.gettempdir()) / "alt-hypothesis")
)
