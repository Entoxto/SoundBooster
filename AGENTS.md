# Agent Notes

## Project

SoundBooster is a Windows-only desktop app for raising effective system volume. The UI is CustomTkinter. Standard Windows volume control uses `pycaw`. Boost above 100% is delegated to EqualizerAPO by writing a `Preamp` config file and including it from EqualizerAPO's main `config.txt`.

## Key Files

- `app/sound_booster.py`: app entrypoint, CustomTkinter UI, settings load/save, pycaw volume control, EqualizerAPO status prompts.
- `app/equalizer_integration.py`: EqualizerAPO detection, optional local installer launch, config path handling, boost config generation.
- `app/icon.py`: generated app icon.
- `scripts/build.py`: PyInstaller build and `SoundBooster-Dist` packaging.
- `scripts/smoke_test.py`: non-GUI runtime check for importing the app, initializing pycaw volume access, and reporting EqualizerAPO status.
- `scripts/download_equalizer_apo.py`: downloads the official x64 Equalizer APO installer as `EqualizerAPO.exe` for release packaging.
- `config/requirements.txt`: Python 3.14 dependency minimums.
- `docs/THIRD_PARTY_NOTICES.txt`: source and license notice for Equalizer APO.
- `start.bat`: user-facing launcher.
- `build.bat`: user-facing release build entrypoint.

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
start.bat
```

Manual equivalent:

```powershell
python -m pip install -r config/requirements.txt
python app/sound_booster.py
```

## Build

```powershell
build.bat
```

The build script creates `dist/SoundBooster.exe`, then copies the final distributable into `SoundBooster-Dist/`.

If `EqualizerAPO.exe` exists in the project root before building, it is bundled/copied. The repository does not include that installer.

To prepare a release package that includes the official x64 Equalizer APO installer:

```powershell
python scripts/download_equalizer_apo.py
python scripts/build.py
```

Keep `THIRD_PARTY_NOTICES.txt` in the release output when bundling the installer.

## Verify

```powershell
python -m py_compile app/sound_booster.py app/equalizer_integration.py app/icon.py scripts/build.py scripts/smoke_test.py scripts/download_equalizer_apo.py
python -m pip install --dry-run -r config/requirements.txt
python scripts/smoke_test.py
```

Manual Windows testing is still required for the GUI, pycaw audio control, EqualizerAPO detection, and writing to the EqualizerAPO config folder.

## Known Pitfalls

- `pycaw` changed the speaker API. Current versions return an `AudioDevice` with `EndpointVolume`; older examples call `.Activate()` directly. Use `get_endpoint_volume()` in `app/sound_booster.py` so both shapes remain supported.
- `scripts/smoke_test.py` initializes the audio backend but does not open the GUI and does not write EqualizerAPO boost config.
- `scripts/download_equalizer_apo.py` pins the expected SHA256 for the official Equalizer APO installer. If the installer version changes, update the URL, checksum, and `docs/THIRD_PARTY_NOTICES.txt` together.

## Constraints

- Do not promise distortion-free audio at high gain.
- Do not assume EqualizerAPO is installed or that `EqualizerAPO.exe` exists in the repo.
- Do not change the EqualizerAPO config format casually. The app writes `sound_booster_gain.txt` and adds `Include: sound_booster_gain.txt`.
- Be careful with permissions: EqualizerAPO usually lives under `Program Files`.
- Keep the app Windows-specific unless the audio backend is intentionally redesigned.
- Do not add unused helper scripts. If a capability is not wired into the app, document why it exists or remove it.
