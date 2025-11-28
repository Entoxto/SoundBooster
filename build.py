"""
Скрипт для сборки приложения SoundBooster в исполняемый файл (.exe) с помощью PyInstaller
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """Проверяет, установлен ли PyInstaller, и устанавливает его при необходимости"""
    try:
        import PyInstaller
        print("PyInstaller уже установлен.")
        return True
    except ImportError:
        print("PyInstaller не установлен. Устанавливаем...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller успешно установлен.")
            return True
        except subprocess.CalledProcessError:
            print("Ошибка установки PyInstaller. Пожалуйста, установите его вручную.")
            return False

def build_executable():
    """Собирает исполняемый файл с помощью PyInstaller"""
    print("Начинаем сборку SoundBooster...")
    
    # Путь к текущему каталогу
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Очищаем предыдущие сборки
    dist_dir = os.path.join(current_dir, "dist")
    build_dir = os.path.join(current_dir, "build")
    spec_file = os.path.join(current_dir, "SoundBooster.spec")
    
    for path in [dist_dir, build_dir, spec_file]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    
    # Подготавливаем добавляемые файлы
    data_files = [
        "--add-data=icon.py;.",
        "--add-data=equalizer_integration.py;.",
    ]
    
    # Добавляем EqualizerAPO.exe, если он существует
    equalizer_path = os.path.join(current_dir, "EqualizerAPO.exe")
    if os.path.exists(equalizer_path):
        data_files.append("--add-data=EqualizerAPO.exe;.")
        print("EqualizerAPO.exe будет включен в дистрибутив")
    else:
        print("ВНИМАНИЕ: EqualizerAPO.exe не найден в текущей директории")
        print("Программа будет собрана без установщика EqualizerAPO")
    
    # Настраиваем команду для PyInstaller
    # Добавляем --collect-all customtkinter для корректной сборки
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SoundBooster",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        "--collect-all=customtkinter",  # Важно для CustomTkinter!
    ] + data_files + ["sound_booster.py"]
    
    # Запускаем PyInstaller
    try:
        subprocess.check_call(pyinstaller_cmd)
        print("Сборка успешно завершена!")
        
        # Создаем каталог для дистрибутива
        dist_output = os.path.join(current_dir, "SoundBooster-Dist")
        if os.path.exists(dist_output):
            shutil.rmtree(dist_output)
        os.mkdir(dist_output)
        
        # Копируем все необходимые файлы в дистрибутив
        shutil.copy(
            os.path.join(dist_dir, "SoundBooster.exe"), 
            os.path.join(dist_output, "SoundBooster.exe")
        )
        
        # Копируем EqualizerAPO.exe в дистрибутив отдельно
        if os.path.exists(equalizer_path):
            shutil.copy(
                equalizer_path,
                os.path.join(dist_output, "EqualizerAPO.exe")
            )
        
        # Создаем README.txt для дистрибутива
        with open(os.path.join(dist_output, "README.txt"), "w", encoding="utf-8") as f:
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
    dependencies = ["pycaw", "comtypes", "pillow", "customtkinter"]
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_").split("==")[0])
        except ImportError:
            print(f"Устанавливаем {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    # Собираем
    build_executable()
    
    print("\nГотово! Нажмите Enter для выхода...")
    input()

if __name__ == "__main__":
    main()
