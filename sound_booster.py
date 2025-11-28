import customtkinter as ctk
from tkinter import messagebox
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import sys
import subprocess
import json
import logging
from PIL import Image, ImageDraw
from icon import get_icon

# Настройка логирования
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soundbooster.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Файл настроек
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

# Импортируем модуль интеграции с EqualizerAPO
try:
    import equalizer_integration
    EQUALIZER_AVAILABLE = True
except ImportError:
    EQUALIZER_AVAILABLE = False
    logger.warning("Модуль equalizer_integration не найден")


def load_settings():
    """Загружает настройки из файла"""
    default_settings = {
        "boost_factor": 1.0,
        "boost_enabled": False,
        "window_x": None,
        "window_y": None
    }
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return {**default_settings, **settings}
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
    
    return default_settings


def save_settings(settings):
    """Сохраняет настройки в файл"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        logger.info("Настройки сохранены")
    except Exception as e:
        logger.error(f"Ошибка сохранения настроек: {e}")


class SoundBooster:
    def __init__(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            logger.info("Инициализация SoundBooster успешна")
            logger.info(f"Текущий уровень громкости: {self.volume.GetMasterVolumeLevelScalar():.2f}")
            
            min_db, max_db, step_db = self.volume.GetVolumeRange()
            logger.info(f"Диапазон громкости: мин {min_db} дБ, макс {max_db} дБ, шаг {step_db} дБ")
            
            self.boost_enabled = False
            self.boost_factor = 1.0
            self.original_volume = self.volume.GetMasterVolumeLevelScalar()
            
            self.equalizer = None
            if EQUALIZER_AVAILABLE:
                self.equalizer = equalizer_integration.EqualizerIntegration()
                if self.equalizer.is_available:
                    logger.info(f"EqualizerAPO найден: {self.equalizer.equalizer_path}")
                else:
                    logger.warning("EqualizerAPO не установлен")
        except Exception as e:
            logger.error(f"Ошибка инициализации SoundBooster: {e}")
            raise
    
    def set_boost_factor(self, factor):
        """Устанавливает коэффициент усиления"""
        self.boost_factor = factor
        
        if self.boost_enabled and self.equalizer and self.equalizer.is_available:
            success, result = self.equalizer.set_boost(factor)
            if success:
                logger.info(f"Усиление EqualizerAPO: {factor:.2f}x")
        
        if self.boost_enabled:
            self.apply_boost()
    
    def toggle_boost(self, enabled):
        """Включает или выключает усиление"""
        if self.boost_enabled == enabled:
            return
        
        self.boost_enabled = enabled
        if enabled:
            self.original_volume = self.volume.GetMasterVolumeLevelScalar()
            
            if self.equalizer and self.equalizer.is_available and self.boost_factor > 1.0:
                success, result = self.equalizer.set_boost(self.boost_factor)
                if success:
                    logger.info(f"Усиление через EqualizerAPO: {self.boost_factor:.2f}x")
                    return
            
            if self.original_volume < 0.95:
                self.apply_boost()
            else:
                self.apply_channel_boost()
        else:
            if self.equalizer and self.equalizer.is_available:
                self.equalizer.set_boost(1.0)
                logger.info("Усиление EqualizerAPO отключено")
            
            try:
                self.volume.SetMasterVolumeLevelScalar(self.original_volume, None)
            except Exception as e:
                logger.error(f"Ошибка восстановления громкости: {e}")
    
    def apply_boost(self):
        """Применяет усиление"""
        try:
            boosted_volume = min(self.original_volume * self.boost_factor, 1.0)
            self.volume.SetMasterVolumeLevelScalar(boosted_volume, None)
            
            current = self.volume.GetMasterVolumeLevelScalar()
            if self.boost_factor > 1.0 and current > 0.95:
                self.apply_channel_boost()
        except Exception as e:
            logger.error(f"Ошибка применения усиления: {e}")
    
    def apply_channel_boost(self):
        """Применяет усиление к каналам"""
        try:
            channel_count = self.volume.GetChannelCount()
            for channel in range(channel_count):
                channel_vol = self.volume.GetChannelVolumeLevelScalar(channel)
                boosted_channel = min(channel_vol * self.boost_factor, 1.0)
                self.volume.SetChannelVolumeLevelScalar(channel, boosted_channel, None)
        except Exception as e:
            logger.error(f"Ошибка усиления каналов: {e}")
    
    def get_current_volume(self):
        """Возвращает текущий уровень громкости"""
        try:
            return int(self.volume.GetMasterVolumeLevelScalar() * 100)
        except:
            return 0
    
    def get_boosted_volume(self):
        """Возвращает усиленный уровень громкости"""
        if not self.boost_enabled:
            return self.get_current_volume(), 100
        
        effective_percent = min(self.boost_factor * 100, 2000)
        current_percent = self.get_current_volume()
        return current_percent, int(effective_percent)


class SoundBoosterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Основные настройки окна
        self.title("SoundBooster")
        self.geometry("450x520")
        self.resizable(False, False)
        
        # Цвета
        self.colors = {
            'bg': '#1a1a2e',
            'card': '#16213e',
            'accent': '#e94560',
            'accent_hover': '#ff6b6b',
            'success': '#4ecca3',
            'text': '#ffffff',
            'text_dim': '#8b8b8b'
        }
        
        self.configure(fg_color=self.colors['bg'])
        
        # Загружаем настройки
        self.settings = load_settings()
        
        # Устанавливаем иконку
        self.set_app_icon()
        
        # Создаем SoundBooster
        self.booster = SoundBooster()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Применяем сохранённые настройки
        self.apply_saved_settings()
        
        # Запускаем мониторинг
        self.volume_monitor_active = True
        self.start_volume_monitor()
        
        # Центрируем окно
        self.restore_window_position()
        
        # Проверка EqualizerAPO
        self.after(1000, self.check_equalizer)
    
    def set_app_icon(self):
        """Устанавливает иконку"""
        try:
            icon = get_icon()
            from PIL import ImageTk
            self.icon_photo = ImageTk.PhotoImage(icon)
            self.iconphoto(True, self.icon_photo)
        except Exception as e:
            logger.error(f"Ошибка иконки: {e}")
    
    def create_widgets(self):
        """Создаёт интерфейс"""
        
        # Главный контейнер
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)
        
        # === ЗАГОЛОВОК ===
        header_frame = ctk.CTkFrame(main, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Иконка
        try:
            icon = get_icon().resize((48, 48))
            from PIL import ImageTk
            self.header_icon = ctk.CTkImage(light_image=icon, dark_image=icon, size=(48, 48))
            icon_label = ctk.CTkLabel(header_frame, image=self.header_icon, text="")
            icon_label.pack(side="left", padx=(0, 15))
        except:
            pass
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y")
        
        title = ctk.CTkLabel(
            title_frame, 
            text="SoundBooster",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=self.colors['accent']
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Усиление звука до 2000%",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_dim']
        )
        subtitle.pack(anchor="w")
        
        # === КАРТОЧКА СТАТУСА ===
        status_card = ctk.CTkFrame(main, fg_color=self.colors['card'], corner_radius=15)
        status_card.pack(fill="x", pady=(0, 20))
        
        status_inner = ctk.CTkFrame(status_card, fg_color="transparent")
        status_inner.pack(fill="x", padx=20, pady=20)
        
        # Громкость
        vol_frame = ctk.CTkFrame(status_inner, fg_color="transparent")
        vol_frame.pack(fill="x", pady=(0, 10))
        
        vol_icon = ctk.CTkLabel(vol_frame, text="🔊", font=ctk.CTkFont(size=20))
        vol_icon.pack(side="left", padx=(0, 10))
        
        self.volume_label = ctk.CTkLabel(
            vol_frame,
            text="Громкость: 100%",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        self.volume_label.pack(side="left")
        
        # Усиление
        boost_frame = ctk.CTkFrame(status_inner, fg_color="transparent")
        boost_frame.pack(fill="x")
        
        boost_icon = ctk.CTkLabel(boost_frame, text="⚡", font=ctk.CTkFont(size=20))
        boost_icon.pack(side="left", padx=(0, 10))
        
        self.boost_label = ctk.CTkLabel(
            boost_frame,
            text="Усиление отключено",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['text_dim']
        )
        self.boost_label.pack(side="left")
        
        # === КАРТОЧКА УПРАВЛЕНИЯ ===
        control_card = ctk.CTkFrame(main, fg_color=self.colors['card'], corner_radius=15)
        control_card.pack(fill="x", pady=(0, 20))
        
        control_inner = ctk.CTkFrame(control_card, fg_color="transparent")
        control_inner.pack(fill="x", padx=20, pady=20)
        
        # Переключатель
        switch_frame = ctk.CTkFrame(control_inner, fg_color="transparent")
        switch_frame.pack(fill="x", pady=(0, 25))
        
        switch_label = ctk.CTkLabel(
            switch_frame,
            text="Включить усиление",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors['text']
        )
        switch_label.pack(side="left")
        
        self.boost_switch = ctk.CTkSwitch(
            switch_frame,
            text="",
            command=self.toggle_boost,
            onvalue=True,
            offvalue=False,
            switch_width=50,
            switch_height=26,
            progress_color=self.colors['accent'],
            button_color=self.colors['text'],
            button_hover_color=self.colors['text']
        )
        self.boost_switch.pack(side="right")
        
        # Слайдер
        slider_label = ctk.CTkLabel(
            control_inner,
            text="Уровень усиления",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_dim']
        )
        slider_label.pack(anchor="w", pady=(0, 10))
        
        # Значение слайдера
        self.slider_value_label = ctk.CTkLabel(
            control_inner,
            text="100%",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['accent']
        )
        self.slider_value_label.pack(pady=(0, 10))
        
        self.boost_slider = ctk.CTkSlider(
            control_inner,
            from_=1.0,
            to=20.0,
            number_of_steps=190,
            command=self.on_slider_change,
            width=380,
            height=20,
            progress_color=self.colors['accent'],
            button_color=self.colors['accent'],
            button_hover_color=self.colors['accent_hover'],
            fg_color=self.colors['bg']
        )
        self.boost_slider.set(1.0)
        self.boost_slider.pack(pady=(0, 5))
        
        # Метки шкалы
        scale_frame = ctk.CTkFrame(control_inner, fg_color="transparent")
        scale_frame.pack(fill="x")
        
        scales = ["100%", "500%", "1000%", "1500%", "2000%"]
        for i, scale in enumerate(scales):
            lbl = ctk.CTkLabel(
                scale_frame,
                text=scale,
                font=ctk.CTkFont(size=10),
                text_color=self.colors['text_dim']
            )
            lbl.pack(side="left", expand=True)
        
        # === КНОПКА СБРОСА ===
        self.reset_btn = ctk.CTkButton(
            main,
            text="⟲  Сбросить к стандартной громкости",
            command=self.reset_volume,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['card'],
            hover_color=self.colors['accent'],
            corner_radius=10
        )
        self.reset_btn.pack(fill="x", pady=(0, 15))
        
        # === СТАТУС EQUALIZER APO ===
        if self.booster.equalizer and self.booster.equalizer.is_available:
            status_text = "✓ EqualizerAPO активен"
            status_color = self.colors['success']
        else:
            status_text = "⚠ Установите EqualizerAPO для >100%"
            status_color = "#ffc93c"
        
        self.status_label = ctk.CTkLabel(
            main,
            text=status_text,
            font=ctk.CTkFont(size=11),
            text_color=status_color
        )
        self.status_label.pack()
        
        # Кнопка установки EqualizerAPO (если не установлен)
        if not (self.booster.equalizer and self.booster.equalizer.is_available):
            install_btn = ctk.CTkButton(
                main,
                text="Установить EqualizerAPO",
                command=self.install_equalizer,
                height=35,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color=self.colors['card'],
                border_width=1,
                border_color=self.colors['accent'],
                text_color=self.colors['accent'],
                corner_radius=8
            )
            install_btn.pack(pady=(10, 0))
    
    def on_slider_change(self, value):
        """Обработчик слайдера"""
        factor = float(value)
        percent = int(factor * 100)
        self.slider_value_label.configure(text=f"{percent}%")
        self.booster.set_boost_factor(factor)
        self.update_labels()
    
    def toggle_boost(self):
        """Переключает усиление"""
        enabled = self.boost_switch.get()
        
        if enabled and self.boost_slider.get() > 1.0:
            if not (self.booster.equalizer and self.booster.equalizer.is_available):
                messagebox.showwarning(
                    "EqualizerAPO не найден",
                    "Для усиления выше 100% нужен EqualizerAPO.\n\n"
                    "Усиление ограничено до 100%."
                )
        
        self.booster.toggle_boost(enabled)
        self.update_labels()
        
        if enabled:
            logger.info(f"Усиление включено: {self.boost_slider.get():.2f}x")
        else:
            logger.info("Усиление выключено")
    
    def reset_volume(self):
        """Сброс громкости"""
        self.boost_switch.deselect()
        self.booster.toggle_boost(False)
        self.boost_slider.set(1.0)
        self.slider_value_label.configure(text="100%")
        self.update_labels()
    
    def update_labels(self):
        """Обновляет метки"""
        current = self.booster.get_current_volume()
        self.volume_label.configure(text=f"Громкость: {current}%")
        
        if self.boost_switch.get():
            _, effective = self.booster.get_boosted_volume()
            self.boost_label.configure(
                text=f"Усиление: {effective}%",
                text_color=self.colors['accent']
            )
        else:
            self.boost_label.configure(
                text="Усиление отключено",
                text_color=self.colors['text_dim']
            )
    
    def start_volume_monitor(self):
        """Мониторинг громкости"""
        def update():
            if self.volume_monitor_active:
                self.update_labels()
                self.after(500, update)
        self.after(500, update)
    
    def apply_saved_settings(self):
        """Применяет настройки"""
        try:
            factor = self.settings.get("boost_factor", 1.0)
            self.boost_slider.set(factor)
            self.slider_value_label.configure(text=f"{int(factor * 100)}%")
            self.booster.set_boost_factor(factor)
            
            if self.settings.get("boost_enabled", False):
                self.boost_switch.select()
                self.booster.toggle_boost(True)
        except Exception as e:
            logger.error(f"Ошибка настроек: {e}")
    
    def save_current_settings(self):
        """Сохраняет настройки"""
        self.settings["boost_factor"] = self.boost_slider.get()
        self.settings["boost_enabled"] = self.boost_switch.get()
        self.settings["window_x"] = self.winfo_x()
        self.settings["window_y"] = self.winfo_y()
        save_settings(self.settings)
    
    def restore_window_position(self):
        """Восстанавливает позицию окна"""
        self.update_idletasks()
        
        x = self.settings.get("window_x")
        y = self.settings.get("window_y")
        
        if x is not None and y is not None:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            w = self.winfo_width()
            h = self.winfo_height()
            
            if 0 <= x <= screen_w - w and 0 <= y <= screen_h - h:
                self.geometry(f'+{x}+{y}')
                return
        
        # Центрируем
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'+{x}+{y}')
    
    def check_equalizer(self):
        """Проверка EqualizerAPO"""
        if self.booster.equalizer and not self.booster.equalizer.is_available:
            response = messagebox.askquestion(
                "EqualizerAPO",
                "Для усиления звука выше 100% нужен EqualizerAPO.\n\n"
                "Установить сейчас?"
            )
            if response == 'yes':
                self.install_equalizer()
    
    def install_equalizer(self):
        """Установка EqualizerAPO"""
        if EQUALIZER_AVAILABLE:
            success, result = equalizer_integration.install_equalizer_apo_from_local()
            if success:
                messagebox.showinfo(
                    "Установка",
                    "После установки EqualizerAPO перезагрузите компьютер\n"
                    "и запустите SoundBooster снова."
                )
            else:
                messagebox.showerror("Ошибка", f"Не удалось запустить установщик:\n{result}")
    
    def on_closing(self):
        """Закрытие"""
        self.volume_monitor_active = False
        self.save_current_settings()
        
        if self.boost_switch.get():
            self.booster.toggle_boost(False)
        
        logger.info("Приложение закрыто")
        self.destroy()


if __name__ == "__main__":
    app = SoundBoosterApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
