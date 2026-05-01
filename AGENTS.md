# Agent Notes

## Project

SoundBooster is a Windows-only desktop app for raising effective system volume. The UI is CustomTkinter. Standard Windows volume control uses `pycaw`. Boost above 100% is delegated to EqualizerAPO by writing a `Preamp` config file and including it from EqualizerAPO's main `config.txt`.

## Key Files

- `sound_booster.py`: app entrypoint, CustomTkinter UI, settings load/save, pycaw volume control, EqualizerAPO status prompts.
- `equalizer_integration.py`: EqualizerAPO detection, optional local installer launch, config path handling, boost config generation.
- `build.py`: PyInstaller build and `SoundBooster-Dist` packaging.
- `icon.py`: generated app icon.
- `requirements.txt`: Python 3.14 dependency minimums.
- `smoke_test.py`: non-GUI runtime check for importing the app, initializing pycaw volume access, and reporting EqualizerAPO status.
- `tools/download_equalizer_apo.py`: downloads the official x64 Equalizer APO installer as `EqualizerAPO.exe` for release packaging.
- `THIRD_PARTY_NOTICES.txt`: source and license notice for Equalizer APO.

## Runtime Files

These are local machine artifacts and should not be committed:

- `settings.json`
- `soundbooster.log`
- `build/`
- `dist/`
- `SoundBooster-Dist/`
- `__pycache__/`
- `EqualizerAPO.exe`

## Run

```powershell
python -m pip install -r requirements.txt
python sound_booster.py
```

## Build

```powershell
python build.py
```

The build script creates `dist/SoundBooster.exe`, then copies the final distributable into `SoundBooster-Dist/`.

If `EqualizerAPO.exe` exists in the project root before building, it is bundled/copied. The repository does not include that installer.

To prepare a release package that includes the official x64 Equalizer APO installer:

```powershell
python tools/download_equalizer_apo.py
python build.py
```

Keep `THIRD_PARTY_NOTICES.txt` in the release output when bundling the installer.

## Verify

```powershell
python -m py_compile sound_booster.py equalizer_integration.py icon.py build.py smoke_test.py tools/download_equalizer_apo.py
python -m pip install --dry-run -r requirements.txt
python smoke_test.py
```

Manual Windows testing is still required for the GUI, pycaw audio control, EqualizerAPO detection, and writing to the EqualizerAPO config folder.

## Known Pitfalls

- `pycaw` changed the speaker API. Current versions return an `AudioDevice` with `EndpointVolume`; older examples call `.Activate()` directly. Use `get_endpoint_volume()` in `sound_booster.py` so both shapes remain supported.
- `smoke_test.py` initializes the audio backend but does not open the GUI and does not write EqualizerAPO boost config.
- `tools/download_equalizer_apo.py` pins the expected SHA256 for the official Equalizer APO installer. If the installer version changes, update the URL, checksum, and `THIRD_PARTY_NOTICES.txt` together.

## Constraints

- Do not promise distortion-free audio at high gain.
- Do not assume EqualizerAPO is installed or that `EqualizerAPO.exe` exists in the repo.
- Do not change the EqualizerAPO config format casually. The app writes `sound_booster_gain.txt` and adds `Include: sound_booster_gain.txt`.
- Be careful with permissions: EqualizerAPO usually lives under `Program Files`.
- Keep the app Windows-specific unless the audio backend is intentionally redesigned.
- Do not add unused helper scripts. If a capability is not wired into the app, document why it exists or remove it.
