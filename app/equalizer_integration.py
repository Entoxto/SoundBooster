"""
Модуль для интеграции с EqualizerAPO для реального усиления звука выше 100%
"""

import os
import subprocess
import winreg as reg
import sys
import time
import tkinter as tk
from tkinter import messagebox
import tempfile
import shutil
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Типичные пути установки EqualizerAPO
POSSIBLE_PATHS = [
    "C:\\Program Files\\EqualizerAPO",
    "C:\\Program Files (x86)\\EqualizerAPO",
]

# Имя файла конфигурации для усиления
BOOST_CONFIG_NAME = "sound_booster_gain.txt"

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)

# Возможные пути к локальному установщику EqualizerAPO
LOCAL_INSTALLER_PATHS = [
    os.path.join(APP_DIR, "EqualizerAPO.exe"),
    os.path.join(PROJECT_ROOT, "EqualizerAPO.exe"),
]


def get_bundled_resource_path(relative_path):
    """Получает путь к ресурсу, который может быть встроен в exe или находиться в директории"""
    try:
        # Если приложение запущено из exe, созданного PyInstaller
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
            resource_path = os.path.join(base_path, relative_path)
            
            # Если файл нужно извлечь из exe, копируем его во временную директорию
            if not os.path.exists(resource_path):
                # Пробуем найти в той же директории, где и exe
                exe_dir = os.path.dirname(sys.executable)
                original_path = os.path.join(exe_dir, relative_path)
                
                if os.path.exists(original_path):
                    return original_path
            
            return resource_path
    except Exception as e:
        logger.error(f"Ошибка при получении пути к ресурсу: {e}")
    
    # Если запущено как обычный скрипт или файл не найден в ресурсах
    local_paths = [
        os.path.join(APP_DIR, relative_path),
        os.path.join(PROJECT_ROOT, relative_path),
    ]
    for local_path in local_paths:
        if os.path.exists(local_path):
            return local_path

    return local_paths[0]


def extract_bundled_installer(target_path=None):
    """Извлекает встроенный установщик EqualizerAPO во временную директорию"""
    try:
        # Пытаемся найти встроенный установщик
        installer_path = get_bundled_resource_path("EqualizerAPO.exe")
        
        if not os.path.exists(installer_path):
            logger.warning("Встроенный установщик EqualizerAPO не найден")
            return False, "Встроенный установщик EqualizerAPO не найден"
        
        # Если путь назначения не указан, используем временную директорию
        if target_path is None:
            temp_dir = tempfile.mkdtemp(prefix="SoundBooster_")
            target_path = os.path.join(temp_dir, "EqualizerAPO.exe")
        
        # Если файл уже существует по указанному пути, используем его
        if installer_path == target_path:
            return True, installer_path
        
        # Копируем файл установщика
        shutil.copy2(installer_path, target_path)
        logger.info(f"Установщик извлечён в {target_path}")
        return True, target_path
    except PermissionError as e:
        logger.error(f"Нет прав доступа для извлечения установщика: {e}")
        return False, f"Нет прав доступа: {e}"
    except IOError as e:
        logger.error(f"Ошибка ввода-вывода при извлечении установщика: {e}")
        return False, f"Ошибка ввода-вывода: {e}"
    except Exception as e:
        logger.error(f"Неожиданная ошибка при извлечении установщика: {e}")
        return False, f"Ошибка при извлечении установщика: {e}"


def is_equalizer_apo_installed():
    """Проверяет, установлен ли EqualizerAPO на компьютере"""
    for path in POSSIBLE_PATHS:
        if os.path.exists(path) and os.path.isdir(path):
            config_path = os.path.join(path, "config")
            if os.path.exists(config_path):
                logger.info(f"EqualizerAPO найден в {path}")
                return path
    
    # Проверим через реестр, если не найдено в стандартных местах
    try:
        key = reg.HKEY_LOCAL_MACHINE
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        with reg.OpenKey(key, key_path) as reg_key:
            for i in range(reg.QueryInfoKey(reg_key)[0]):
                try:
                    subkey_name = reg.EnumKey(reg_key, i)
                    with reg.OpenKey(reg_key, subkey_name) as subkey:
                        try:
                            display_name = reg.QueryValueEx(subkey, "DisplayName")[0]
                            if "EqualizerAPO" in display_name:
                                install_location = reg.QueryValueEx(subkey, "InstallLocation")[0]
                                logger.info(f"EqualizerAPO найден через реестр в {install_location}")
                                return install_location
                        except FileNotFoundError:
                            # Ключ DisplayName или InstallLocation не существует
                            continue
                        except OSError as e:
                            logger.debug(f"Ошибка чтения подключа {subkey_name}: {e}")
                            continue
                except OSError as e:
                    logger.debug(f"Ошибка перечисления ключей реестра: {e}")
                    continue
    except FileNotFoundError:
        logger.debug("Ключ реестра Uninstall не найден")
    except PermissionError as e:
        logger.warning(f"Нет прав доступа к реестру: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке реестра: {e}")
    
    logger.info("EqualizerAPO не найден в системе")
    return None


def get_config_path(equalizer_path):
    """Возвращает путь к папке с конфигурацией"""
    return os.path.join(equalizer_path, "config")


def create_boost_config(equalizer_path, boost_factor):
    """Создает файл конфигурации для усиления звука"""
    try:
        config_path = get_config_path(equalizer_path)
        boost_file = os.path.join(config_path, BOOST_CONFIG_NAME)
        
        # Преобразуем коэффициент усиления в децибелы
        # Формула: dB = 20 * log10(boost_factor)
        import math
        db_gain = 20 * math.log10(boost_factor)
        
        # Создаем файл конфигурации
        with open(boost_file, 'w', encoding='utf-8') as f:
            f.write(f"Preamp: {db_gain:.2f} dB\n")
            f.write("# Конфигурация создана SoundBooster\n")
            f.write("# Чем выше значение Preamp, тем сильнее усиление\n")
            f.write("# Можно изменить вручную в Peace GUI или через это приложение\n")
        
        logger.info(f"Создан файл усиления: {boost_file} с gain={db_gain:.2f} dB")
        
        # Проверяем, включен ли наш файл в основную конфигурацию
        main_config = os.path.join(config_path, "config.txt")
        
        if os.path.exists(main_config):
            # Проверяем, есть ли уже Include для нашего файла
            include_line = f"Include: {BOOST_CONFIG_NAME}"
            need_to_add = True
            
            with open(main_config, 'r', encoding='utf-8') as f:
                content = f.read()
                if include_line in content:
                    need_to_add = False
            
            # Добавляем Include, если его нет
            if need_to_add:
                with open(main_config, 'a', encoding='utf-8') as f:
                    f.write(f"\n{include_line}\n")
                logger.info(f"Добавлена строка Include в {main_config}")
        else:
            # Создаем новый config.txt
            with open(main_config, 'w', encoding='utf-8') as f:
                f.write(f"Include: {BOOST_CONFIG_NAME}\n")
            logger.info(f"Создан новый файл конфигурации: {main_config}")
        
        return True, boost_file
    except PermissionError as e:
        logger.error(f"Нет прав доступа для записи конфигурации: {e}")
        return False, f"Нет прав доступа: {e}"
    except IOError as e:
        logger.error(f"Ошибка ввода-вывода при создании конфигурации: {e}")
        return False, f"Ошибка ввода-вывода: {e}"
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании конфигурации: {e}")
        return False, str(e)


def set_boost_level(equalizer_path, boost_factor):
    """Устанавливает уровень усиления"""
    if boost_factor < 1.0:
        boost_factor = 1.0  # Минимальное усиление 0 дБ (100%)
    
    success, result = create_boost_config(equalizer_path, boost_factor)
    return success, result


def install_equalizer_apo_from_local():
    """Устанавливает EqualizerAPO из локального файла или встроенного ресурса"""
    # Сначала проверяем, существует ли установщик в текущей директории
    installer_path = None
    for local_installer_path in LOCAL_INSTALLER_PATHS:
        if os.path.exists(local_installer_path):
            installer_path = local_installer_path
            logger.info(f"Используется локальный установщик: {installer_path}")
            break

    if installer_path is None:
        # Если локальный файл не найден, пробуем извлечь из ресурсов
        success, result = extract_bundled_installer()
        if not success:
            return False, result
        installer_path = result
    
    try:
        # Запускаем установщик
        subprocess.Popen(installer_path, shell=True)
        logger.info("Установщик EqualizerAPO запущен")
        return True, "Установщик EqualizerAPO запущен"
    except FileNotFoundError as e:
        logger.error(f"Установщик не найден: {e}")
        return False, f"Установщик не найден: {e}"
    except PermissionError as e:
        logger.error(f"Нет прав для запуска установщика: {e}")
        return False, f"Нет прав для запуска: {e}"
    except Exception as e:
        logger.error(f"Ошибка запуска установщика: {e}")
        return False, f"Ошибка запуска установщика: {e}"


def suggest_equalizer_apo(parent=None):
    """Показывает диалог с предложением установить EqualizerAPO из локального файла"""
    msg = ("Для усиления звука выше 100% необходимо установить EqualizerAPO.\n\n"
           "EqualizerAPO - мощный системный эквалайзер, который позволяет:\n"
           "- Усиливать звук выше стандартного максимума\n"
           "- Настраивать частотные характеристики звука\n"
           "- Применять различные звуковые эффекты\n\n"
           "Хотите установить EqualizerAPO из локального файла?")
    
    if parent:
        response = messagebox.askquestion("Установка EqualizerAPO", msg, parent=parent)
        if response == 'yes':
            success, message = install_equalizer_apo_from_local()
            if not success:
                messagebox.showerror("Ошибка", message, parent=parent)
                return False
            
            # Инструкции по установке
            install_msg = ("После запуска установщика EqualizerAPO:\n\n"
                         "1. Следуйте инструкциям установщика\n"
                         "2. При установке выберите ваше звуковое устройство\n"
                         "3. Завершите установку и перезагрузите компьютер\n"
                         "4. После перезагрузки запустите SoundBooster снова\n\n"
                         "EqualizerAPO будет автоматически настроен для усиления звука.")
            messagebox.showinfo("Инструкции по установке", install_msg, parent=parent)
            return True
    else:
        print(msg)
        response = input("Установить EqualizerAPO? (y/n): ")
        if response.lower() == 'y':
            success, message = install_equalizer_apo_from_local()
            if not success:
                print(f"Ошибка: {message}")
                return False
            return True
    
    return False


class EqualizerIntegration:
    """Класс для интеграции с EqualizerAPO"""
    
    def __init__(self):
        self.equalizer_path = is_equalizer_apo_installed()
        self.is_available = self.equalizer_path is not None
        self.current_boost = 1.0
        
        if self.is_available:
            logger.info(f"EqualizerIntegration инициализирован, путь: {self.equalizer_path}")
        else:
            logger.info("EqualizerIntegration: EqualizerAPO не найден")
    
    def set_boost(self, boost_factor):
        """Устанавливает коэффициент усиления"""
        if not self.is_available:
            logger.warning("Попытка установить усиление, но EqualizerAPO не установлен")
            return False, "EqualizerAPO не установлен"
        
        self.current_boost = boost_factor
        logger.info(f"Установка коэффициента усиления: {boost_factor:.2f}x")
        return set_boost_level(self.equalizer_path, boost_factor)
    
    def open_equalizer_interface(self):
        """Открывает интерфейс EqualizerAPO (Peace GUI, если установлен)"""
        if not self.is_available:
            logger.warning("Попытка открыть интерфейс, но EqualizerAPO не установлен")
            return False, "EqualizerAPO не установлен"
        
        # Сначала пробуем открыть Peace GUI (если установлен)
        peace_path = os.path.join(self.equalizer_path, "Peace.exe")
        if os.path.exists(peace_path):
            try:
                subprocess.Popen(peace_path)
                logger.info("Peace GUI запущен")
                return True, "Peace GUI запущен"
            except Exception as e:
                logger.error(f"Ошибка запуска Peace GUI: {e}")
        
        # Если Peace не установлен, открываем папку с конфигурацией
        try:
            config_path = get_config_path(self.equalizer_path)
            os.startfile(config_path)
            logger.info(f"Открыта папка с конфигурацией: {config_path}")
            return True, "Открыта папка с конфигурацией"
        except Exception as e:
            logger.error(f"Ошибка открытия папки конфигурации: {e}")
            return False, f"Ошибка: {e}"


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Пример использования
    equalizer = EqualizerIntegration()
    
    if equalizer.is_available:
        print(f"EqualizerAPO установлен в {equalizer.equalizer_path}")
        
        # Устанавливаем усиление 200%
        success, result = equalizer.set_boost(2.0)
        print(f"Установка усиления: {'успешно' if success else 'ошибка'}")
        if not success:
            print(f"Ошибка: {result}")
        
        # Открываем интерфейс
        equalizer.open_equalizer_interface()
    else:
        print("EqualizerAPO не установлен")
        suggest_equalizer_apo()
