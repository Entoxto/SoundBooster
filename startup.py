import os
import sys
import winreg as reg
import ctypes
import tkinter as tk
from tkinter import messagebox

def is_admin():
    """Проверяет, запущен ли скрипт с правами администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_to_startup(file_path=None):
    """Добавляет SoundBooster в автозагрузку Windows"""
    if file_path is None:
        # Если путь не указан, используем путь до текущего скрипта
        file_path = os.path.abspath(sys.argv[0])
        # Заменяем startup.py на sound_booster.py
        if os.path.basename(file_path).lower() == "startup.py":
            file_path = os.path.join(os.path.dirname(file_path), "sound_booster.py")

    # Путь для Python интерпретатора
    python_path = sys.executable
    
    # Полная команда для запуска приложения
    startup_command = f'"{python_path}" "{file_path}"'
    
    # Открываем ключ реестра для автозагрузки
    key = reg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        with reg.OpenKey(key, key_path, 0, reg.KEY_WRITE) as registry_key:
            reg.SetValueEx(registry_key, "SoundBooster", 0, reg.REG_SZ, startup_command)
        return True
    except Exception as e:
        print(f"Ошибка при добавлении в автозагрузку: {e}")
        return False

def remove_from_startup():
    """Удаляет SoundBooster из автозагрузки Windows"""
    key = reg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        with reg.OpenKey(key, key_path, 0, reg.KEY_WRITE) as registry_key:
            reg.DeleteValue(registry_key, "SoundBooster")
        return True
    except Exception as e:
        print(f"Ошибка при удалении из автозагрузки: {e}")
        return False

def is_in_startup():
    """Проверяет, добавлен ли SoundBooster в автозагрузку"""
    key = reg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        with reg.OpenKey(key, key_path, 0, reg.KEY_READ) as registry_key:
            reg.QueryValueEx(registry_key, "SoundBooster")
        return True
    except Exception:
        return False

def create_gui():
    """Создает простой графический интерфейс для управления автозагрузкой"""
    root = tk.Tk()
    root.title("SoundBooster - Автозагрузка")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # Центрируем окно
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True, fill=tk.BOTH)
    
    label = tk.Label(
        frame, 
        text="Настройка автозапуска SoundBooster", 
        font=("Arial", 12, "bold")
    )
    label.pack(pady=10)
    
    status_text = "SoundBooster " + ("добавлен" if is_in_startup() else "не добавлен") + " в автозагрузку."
    status_label = tk.Label(frame, text=status_text)
    status_label.pack(pady=10)
    
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)
    
    add_button = tk.Button(
        button_frame, 
        text="Добавить в автозагрузку",
        command=lambda: toggle_startup(True, status_label),
        width=20
    )
    add_button.pack(side=tk.LEFT, padx=5)
    
    remove_button = tk.Button(
        button_frame, 
        text="Удалить из автозагрузки",
        command=lambda: toggle_startup(False, status_label),
        width=20
    )
    remove_button.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

def toggle_startup(add, status_label):
    """Включает или выключает автозагрузку и обновляет статус"""
    success = False
    
    if add:
        success = add_to_startup()
        if success:
            messagebox.showinfo("SoundBooster", "SoundBooster добавлен в автозагрузку.")
            status_label.config(text="SoundBooster добавлен в автозагрузку.")
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить в автозагрузку. Попробуйте запустить с правами администратора.")
    else:
        success = remove_from_startup()
        if success:
            messagebox.showinfo("SoundBooster", "SoundBooster удален из автозагрузки.")
            status_label.config(text="SoundBooster не добавлен в автозагрузку.")
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить из автозагрузки. Попробуйте запустить с правами администратора.")

if __name__ == "__main__":
    # Проверяем, нужны ли права администратора
    if not is_admin():
        # Если нужны, перезапускаем с правами администратора
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        # Запускаем интерфейс
        create_gui() 