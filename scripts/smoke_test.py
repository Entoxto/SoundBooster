"""Smoke checks for SoundBooster without opening the GUI."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
sys.path.insert(0, str(APP_DIR))

# Import after adjusting sys.path so the test works from scripts/.
from sound_booster import SoundBooster


def main() -> int:
    try:
        booster = SoundBooster()
        current_volume = booster.get_current_volume()
    except Exception:
        traceback.print_exc()
        return 1

    equalizer_status = "unavailable"
    if booster.equalizer and booster.equalizer.is_available:
        equalizer_status = f"available at {booster.equalizer.equalizer_path}"

    print("SoundBooster smoke test passed")
    print(f"Current volume: {current_volume}%")
    print(f"EqualizerAPO: {equalizer_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
