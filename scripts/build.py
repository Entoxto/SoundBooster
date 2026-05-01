"""
Скрипт для сборки приложения SoundBooster в исполняемый файл (.exe) с помощью PyInstaller
"""

import sys
import subprocess
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"

def check_pyinstaller():
    """Проверяет, установлен ли PyInstaller, и устанавливает его при необходимости"""
    try:
        import PyInstaller
        print("PyInstaller уже установлен.")
        return True
    except ImportError:
        print("PyInstaller не установлен. Устанавливаем...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=6.20.0"])
            print("PyInstaller успешно установлен.")
            return True
        except subprocess.CalledProcessError:
            print("Ошибка установки PyInstaller. Пожалуйста, установите его вручную.")
            return False

def build_executable():
    """Собирает исполняемый файл с помощью PyInstaller"""
    print("Начинаем сборку SoundBooster...")
    
    # Очищаем предыдущие сборки
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    spec_file = PROJECT_ROOT / "SoundBooster.spec"
    
    for path in [dist_dir, build_dir, spec_file]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    # Подготавливаем добавляемые файлы
    data_files = [
        f"--add-data={APP_DIR / 'icon.py'};.",
        f"--add-data={APP_DIR / 'equalizer_integration.py'};.",
    ]
    
    # Добавляем EqualizerAPO.exe, если он существует
    equalizer_path = PROJECT_ROOT / "EqualizerAPO.exe"
    if equalizer_path.exists():
        data_files.append(f"--add-data={equalizer_path};.")
        print("EqualizerAPO.exe будет включен в дистрибутив")
    else:
        print("ВНИМАНИЕ: EqualizerAPO.exe не найден в текущей директории")
        print("Программа будет собрана без установщика EqualizerAPO")
        print("Для релизной сборки можно скачать официальный установщик:")
        print("python scripts/download_equalizer_apo.py")
    
    # Настраиваем команду для PyInstaller
    # Добавляем --collect-all customtkinter для корректной сборки
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SoundBooster",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        "--collect-all=customtkinter",  # Важно для CustomTkinter!
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(PROJECT_ROOT),
    ] + data_files + [str(APP_DIR / "sound_booster.py")]
    
    # Запускаем PyInstaller
    try:
        subprocess.check_call(pyinstaller_cmd, cwd=PROJECT_ROOT)
        print("Сборка успешно завершена!")
        
        # Создаем каталог для дистрибутива
        dist_output = PROJECT_ROOT / "SoundBooster-Dist"
        if dist_output.exists():
            shutil.rmtree(dist_output)
        dist_output.mkdir()
        
        # Копируем все необходимые файлы в дистрибутив
        shutil.copy(
            dist_dir / "SoundBooster.exe",
            dist_output / "SoundBooster.exe"
        )
        
        # Копируем EqualizerAPO.exe в дистрибутив отдельно
        if equalizer_path.exists():
            shutil.copy(
                equalizer_path,
                dist_output / "EqualizerAPO.exe"
            )

        notices_path = DOCS_DIR / "THIRD_PARTY_NOTICES.txt"
        if notices_path.exists():
            shutil.copy(
                notices_path,
                dist_output / "THIRD_PARTY_NOTICES.txt"
            )
        
        # Создаем README.txt для дистрибутива
        with open(dist_output / "README.txt", "w", encoding="utf-8") as f:
            f.write("""SoundBooster для Windows
======================

Приложение для усиления громкости системы Windows выше стандартного максимума (до 2000%).
Версия 3.0.0 - Современный интерфейс

Инструкция:
1. Запустите SoundBooster.exe
2. При первом запуске установите EqualizerAPO для усиления >100%
3. Перезагрузите компьютер после установки EqualizerAPO
4. Готово! Теперь можно усиливать звук до 2000%

Управление:
- Включите усиление переключателем
- Выберите уровень усиления слайдером (100% - 2000%)
- Настройки сохраняются автоматически

Примечание: При первом запуске Windows может показать предупреждение.
Нажмите "Подробнее" → "Выполнить в любом случае"
""")
        
        print(f"\nДистрибутив создан: {dist_output}")
        print("Можете распространять папку SoundBooster-Dist")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке: {e}")
        return False

def main():
    """Основная функция"""
    # Проверяем PyInstaller
    if not check_pyinstaller():
        print("Сборка прервана.")
        return
    
    # Проверяем зависимости
    print("Проверяем зависимости...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r",
        str(CONFIG_DIR / "requirements.txt")
    ])
    
    # Собираем
    build_executable()
    
    print("\nГотово!")

if __name__ == "__main__":
    main()
