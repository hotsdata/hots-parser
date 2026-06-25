"""Helpers for loading Blizzard's heroprotocol submodule under Python 3."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
HEROPROTOCOL_ROOT = REPO_ROOT / "heroprotocol"


def ensure_heroprotocol_path() -> None:
    """Make the checked-out heroprotocol submodule importable."""
    path = str(HEROPROTOCOL_ROOT)
    if path not in sys.path:
        sys.path.insert(0, path)


def get_mpyq_archive_class():
    import mpyq

    return mpyq.MPQArchive


def get_header_protocol():
    """Return a protocol module capable of decoding replay headers."""
    ensure_heroprotocol_path()
    from heroprotocol.versions import latest

    return latest()


def get_protocol_for_build(base_build: int):
    """Return the exact or nearest older generated protocol for a replay build.

    Blizzard sometimes releases replay builds newer than the latest generated
    protocol in the upstream repository. In that case, the nearest older
    protocol is usually still able to decode stable sections such as details,
    init data, attributes, and tracker events. The returned tuple is:

        protocol_module, selected_build, is_fallback
    """
    ensure_heroprotocol_path()
    from heroprotocol import versions

    try:
        return versions.build(base_build), base_build, False
    except Exception:
        available = sorted(int(re.search(r"protocol(\d+)\.py$", filename).group(1)) for filename in versions.list_all())
        older_or_equal = [build for build in available if build <= base_build]
        if not older_or_equal:
            raise
        selected_build = older_or_equal[-1]
        return versions.build(selected_build), selected_build, True
