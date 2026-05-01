"""
Download the official Equalizer APO installer used for SoundBooster releases.

The installer is intentionally not committed to git. Run this script before a
release build if the release package should include EqualizerAPO.exe.
"""

from __future__ import annotations

import hashlib
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
EQUALIZER_APO_SHA256 = (
    "7403be7427bbe1936a40dded082829b6e217fc4f5990fee5cba501f0ae055afa"
)
OUTPUT_FILENAME = "EqualizerAPO.exe"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / OUTPUT_FILENAME
    temp_path = output_path.with_suffix(output_path.suffix + ".download")

    print(f"Downloading Equalizer APO {EQUALIZER_APO_VERSION} x64...")
    print(f"Source: {EQUALIZER_APO_URL}")
    print(f"Target: {output_path}")

    temp_path.unlink(missing_ok=True)

    request = urllib.request.Request(
        EQUALIZER_APO_URL,
        headers={"User-Agent": "SoundBooster release downloader"},
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            temp_path.write_bytes(response.read())
    except urllib.error.URLError as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Could not write installer: {exc}", file=sys.stderr)
        return 1

    actual_sha256 = sha256_file(temp_path)
    if actual_sha256 != EQUALIZER_APO_SHA256:
        temp_path.unlink(missing_ok=True)
        print("Downloaded installer checksum mismatch.", file=sys.stderr)
        print(f"Expected: {EQUALIZER_APO_SHA256}", file=sys.stderr)
        print(f"Actual:   {actual_sha256}", file=sys.stderr)
        return 1

    try:
        temp_path.replace(output_path)
    except OSError as exc:
        temp_path.unlink(missing_ok=True)
        print(f"Could not finalize installer: {exc}", file=sys.stderr)
        return 1

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Saved {output_path.name} ({size_mb:.1f} MB)")
    print(f"SHA256: {actual_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
