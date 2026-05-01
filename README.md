# SoundBooster

SoundBooster — небольшое Windows-приложение для увеличения эффективной громкости системы выше стандартных 100%.

Приложение работает в два слоя:

- управляет системной громкостью Windows через `pycaw`;
- для усиления выше 100% использует EqualizerAPO и записывает для него `Preamp`-конфигурацию.

SoundBooster не является аудиодрайвером и не заменяет EqualizerAPO. Для усиления выше 100% EqualizerAPO должен быть установлен и включен для нужного устройства вывода.

## Скачать

Для обычного использования скачайте готовый архив из раздела [Releases](https://github.com/Entoxto/SoundBooster/releases).

Ожидаемый состав релизного архива:

```txt
SoundBooster-Dist/
├── SoundBooster.exe
├── EqualizerAPO.exe
├── THIRD_PARTY_NOTICES.txt
└── README.txt
```

Запустите `SoundBooster.exe`. Если EqualizerAPO уже установлен, SoundBooster не будет запускать установщик. Если EqualizerAPO не найден, приложение предложит установить его из файла `EqualizerAPO.exe`, который идет рядом в релизном архиве.

## Текущее состояние

Проект предназначен только для Windows. Текущая среда разработки использует Python 3.14.

Приложение можно запускать из исходников или собирать в `SoundBooster.exe` через PyInstaller. Готовый exe можно переносить между папками, но основная функция усиления выше 100% все равно зависит от установленного EqualizerAPO на конкретном компьютере.

## Возможности

- Темный интерфейс на CustomTkinter.
- Слайдер усиления от 100% до 2000%.
- Сохранение состояния усиления, уровня усиления и позиции окна в `settings.json`.
- Логи работы в `soundbooster.log`.
- Поиск EqualizerAPO в стандартных папках установки и через реестр Windows.
- Запуск локального установщика `EqualizerAPO.exe`, если этот файл лежит рядом с приложением или был добавлен в сборку.

## Ограничения и безопасность

Высокое усиление может вызывать искажения, клиппинг или слишком громкий звук. Начинайте с небольших значений и повышайте уровень постепенно.

При включении усиления SoundBooster создает файл EqualizerAPO:

```txt
Preamp: <gain> dB
```

И добавляет в основной `config.txt` строку:

```txt
Include: sound_booster_gain.txt
```

Запись в папку конфигурации EqualizerAPO может требовать прав, потому что EqualizerAPO обычно установлен в `Program Files`.

## Требования

- Windows 10 или Windows 11.
- Python 3.14 для разработки в текущем состоянии проекта.
- EqualizerAPO для усиления выше 100%.
- Зависимости из `config/requirements.txt`.

Установщик EqualizerAPO не хранится в этом репозитории. Если нужно, чтобы приложение предлагало установку EqualizerAPO, положите `EqualizerAPO.exe` в корень проекта перед запуском или сборкой.

Для релизной сборки можно скачать официальный x64-установщик EqualizerAPO:

```powershell
python scripts/download_equalizer_apo.py
```

Скрипт сохраняет установщик как `EqualizerAPO.exe`, проверяет SHA256 и только после этого использует файл для сборки.

## Запуск из исходников

```powershell
git clone https://github.com/Entoxto/SoundBooster.git
cd SoundBooster
start.bat
```

`start.bat` установит зависимости из `config/requirements.txt` и запустит приложение из папки `app/`.

Если нужен ручной запуск без батника:

```powershell
python -m pip install -r config/requirements.txt
python app/sound_booster.py
```

## Сборка

```powershell
build.bat
```

`build.bat` скачивает официальный установщик EqualizerAPO, проверяет SHA256 и собирает релизную папку.

Если нужна ручная сборка без батника:

```powershell
python scripts/download_equalizer_apo.py
python scripts/build.py
```

PyInstaller сначала создает `dist/SoundBooster.exe`. После этого `build.py` собирает итоговую папку для распространения:

```txt
SoundBooster-Dist/
├── SoundBooster.exe
├── EqualizerAPO.exe    # только если файл был в корне проекта до сборки
├── THIRD_PARTY_NOTICES.txt
└── README.txt
```

Для распространения используйте `SoundBooster-Dist`, а не только сырой `dist`.

## Структура проекта

```txt
SoundBooster/
├── start.bat                 # Пользовательский запуск приложения из исходников
├── build.bat                 # Пользовательская сборка релизной папки
├── app/
│   ├── sound_booster.py          # Точка входа, UI, настройки, управление громкостью через pycaw
│   ├── equalizer_integration.py  # Поиск EqualizerAPO, запуск установщика, запись конфигов
│   └── icon.py                   # Генерация иконки приложения
├── scripts/
│   ├── build.py                  # Сборка exe через PyInstaller
│   ├── download_equalizer_apo.py # Загрузка официального установщика EqualizerAPO
│   └── smoke_test.py             # Проверка без запуска GUI
├── config/
│   └── requirements.txt          # Зависимости Python
├── docs/
│   └── THIRD_PARTY_NOTICES.txt   # Источник и лицензия стороннего установщика
└── README.md
```

Для обычной работы в корне нужны только два сценария:

- `start.bat` — запустить приложение из исходников.
- `build.bat` — скачать EqualizerAPO и собрать `SoundBooster-Dist/`.

Локальные файлы, которые не нужно коммитить:

- `settings.json`
- `soundbooster.log`
- `build/`
- `dist/`
- `SoundBooster-Dist/`
- `EqualizerAPO.exe`

## Частые проблемы

### Усиление выше 100% не работает

Проверьте, что EqualizerAPO установлен, включен для правильного устройства вывода и что компьютер был перезагружен после установки или изменения устройства.

### Приложение не может установить EqualizerAPO

SoundBooster не скачивает установщик сам. Он только запускает локальный файл `EqualizerAPO.exe`. Положите этот файл в корень проекта перед запуском из исходников или перед сборкой.

Для подготовки релиза используйте:

```powershell
python scripts/download_equalizer_apo.py
python scripts/build.py
```

Если EqualizerAPO уже установлен на компьютере пользователя, SoundBooster не запускает установщик повторно.

### Антивирус предупреждает об exe

PyInstaller-сборки иногда вызывают ложные срабатывания. Если бинарник не вызывает доверия, запускайте проект из исходников и проверьте код перед использованием.

## Проверки для разработки

Быстрая проверка синтаксиса:

```powershell
python -m py_compile app/sound_booster.py app/equalizer_integration.py app/icon.py scripts/build.py scripts/smoke_test.py scripts/download_equalizer_apo.py
```

Проверка разрешения зависимостей под текущую версию Python:

```powershell
python -m pip install --dry-run -r config/requirements.txt
```

Smoke-проверка без запуска GUI:

```powershell
python scripts/smoke_test.py
```

Интерфейс, работу `pycaw`, обнаружение EqualizerAPO и запись в конфиг EqualizerAPO нужно проверять вручную на Windows с реальным аудиоустройством.

## Лицензия

MIT License.
