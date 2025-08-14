"""jinpy-utils: A small set of reusable utilities.

Public APIs are organized under subpackages:
- `jinpy_utils.base`: Structured exceptions and helpers
- `jinpy_utils.logger`: Structured, async-capable logging with backends
- `jinpy_utils.utils`: Small cross-cutting helpers (e.g., timing)
"""

from jinpy_utils.utils import get_current_datetime

__all__: list[str] = ["get_current_datetime"]
