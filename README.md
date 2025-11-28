# 🔊 SoundBooster

<div align="center">

![SoundBooster](https://img.shields.io/badge/Windows-10%2F11-blue?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Усиление громкости Windows до 2000%**

[Скачать](#-установка) • [Возможности](#-возможности) • [Скриншоты](#-скриншоты) • [FAQ](#-faq)

</div>

---

## 📖 О программе

**SoundBooster** — приложение для усиления громкости системы Windows выше стандартного максимума. Когда 100% громкости недостаточно — SoundBooster поможет!

Использует интеграцию с [EqualizerAPO](https://sourceforge.net/projects/equalizerapo/) для реального программного усиления аудиосигнала без искажений.

## ✨ Возможности

- 🎚️ **Усиление до 2000%** — реальное увеличение громкости через EqualizerAPO
- 🌙 **Современный интерфейс** — тёмная тема, плавные анимации
- 💾 **Сохранение настроек** — запоминает уровень усиления между сессиями
- 🚀 **Портативность** — один exe файл, не требует установки
- 🔧 **Встроенный установщик** — EqualizerAPO устанавливается в один клик

## 📸 Скриншоты

<div align="center">
<img src="https://via.placeholder.com/400x500/1a1a2e/e94560?text=SoundBooster+UI" alt="SoundBooster Interface" width="400">
</div>

## 📥 Установка

### Способ 1: Скачать готовый exe (рекомендуется)

1. Перейдите в раздел [**Releases**](../../releases)
2. Скачайте `SoundBooster.zip`
3. Распакуйте и запустите `SoundBooster.exe`
4. При первом запуске установите EqualizerAPO (программа предложит)
5. **Перезагрузите компьютер** после установки EqualizerAPO

### Способ 2: Запуск из исходников

```bash
# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/SoundBooster.git
cd SoundBooster

# Установить зависимости
pip install -r requirements.txt

# Запустить
python sound_booster.py
```

### Способ 3: Собрать exe самостоятельно

```bash
# Установить зависимости
pip install -r requirements.txt

# Собрать exe
python build.py
```

Готовый exe появится в папке `dist/`

## 🎯 Использование

1. **Запустите** SoundBooster
2. **Включите усиление** переключателем
3. **Выберите уровень** слайдером (100% - 2000%)
4. Готово! Настройки сохраняются автоматически

## ⚙️ Требования

- **Windows 10/11**
- **EqualizerAPO** (для усиления >100%) — устанавливается автоматически

### Для запуска из исходников:
- Python 3.8+
- Зависимости из `requirements.txt`

## 📁 Структура проекта

```
SoundBooster/
├── sound_booster.py       # Главное приложение
├── equalizer_integration.py # Интеграция с EqualizerAPO
├── icon.py                # Генерация иконки
├── startup.py             # Настройка автозагрузки
├── build.py               # Скрипт сборки в exe
├── requirements.txt       # Зависимости Python
└── README.md
```

## ❓ FAQ

<details>
<summary><b>Усиление выше 100% не работает</b></summary>

1. Убедитесь, что EqualizerAPO установлен
2. **Перезагрузите компьютер** после установки
3. При установке EqualizerAPO выберите правильное аудиоустройство

</details>

<details>
<summary><b>Как удалить EqualizerAPO?</b></summary>

Панель управления → Программы и компоненты → EqualizerAPO → Удалить

</details>

<details>
<summary><b>Безопасно ли усиление 2000%?</b></summary>

Да, но используйте осторожно. Высокий уровень усиления может вызвать:
- Искажения звука
- Дискомфорт при прослушивании в наушниках

Рекомендуем начинать с 150-200% и постепенно увеличивать.

</details>

<details>
<summary><b>Антивирус блокирует exe</b></summary>

Это ложное срабатывание (False Positive). PyInstaller-приложения часто вызывают такую реакцию. Вы можете:
- Добавить в исключения антивируса
- Запустить из исходников (`python sound_booster.py`)

</details>

## 🛠️ Технологии

- **Python 3.12** — основной язык
- **CustomTkinter** — современный UI
- **pycaw** — Windows Audio API
- **EqualizerAPO** — системный эквалайзер для усиления
- **PyInstaller** — сборка в exe

## 📄 Лицензия

MIT License — используйте свободно!

## 🤝 Вклад

Pull requests приветствуются! Для крупных изменений сначала откройте issue.

---

<div align="center">

**⭐ Если проект полезен — поставьте звезду!**

</div>
