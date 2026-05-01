"""
Download the official Equalizer APO installer used for SoundBooster releases.

The installer is intentionally not committed to git. Run this script before a
release build if the release package should include EqualizerAPO.exe.
"""

from __future__ import annotations

import sys
import urllib.error
import urllib.request
from pathlib import Path


EQUALIZER_APO_VERSION = "1.4.2"
EQUALIZER_APO_FILENAME = f"EqualizerAPO-x64-{EQUALIZER_APO_VERSION}.exe"
EQUALIZER_APO_URL = (
    "https://sourceforge.net/projects/equalizerapo/files/"
    f"{EQUALIZER_APO_VERSION}/{EQUALIZER_APO_FILENAME}/download"
)
OUTPUT_FILENAME = "EqualizerAPO.exe"


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / OUTPUT_FILENAME

    print(f"Downloading Equalizer APO {EQUALIZER_APO_VERSION} x64...")
    print(f"Source: {EQUALIZER_APO_URL}")
    print(f"Target: {output_path}")

    request = urllib.request.Request(
        EQUALIZER_APO_URL,
        headers={"User-Agent": "SoundBooster release downloader"},
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            output_path.write_bytes(response.read())
    except urllib.error.URLError as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Saved {output_path.name} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
