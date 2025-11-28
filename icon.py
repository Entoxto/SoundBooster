"""
Модуль для создания иконки приложения SoundBooster
"""

from PIL import Image, ImageDraw
import io
import base64


def create_icon_image(size=64):
    """Создаёт иконку приложения программно"""
    # Создаём изображение с прозрачным фоном
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Цвета
    bg_color = (26, 26, 46, 255)  # #1a1a2e
    accent_color = (233, 69, 96, 255)  # #e94560
    light_color = (78, 204, 163, 255)  # #4ecca3
    
    # Рисуем круглый фон
    padding = 2
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=bg_color
    )
    
    # Рисуем динамик (speaker icon)
    center_x = size // 2
    center_y = size // 2
    
    # Основа динамика (прямоугольник)
    speaker_width = size // 6
    speaker_height = size // 4
    draw.rectangle(
        [
            center_x - speaker_width - size // 8,
            center_y - speaker_height // 2,
            center_x - size // 8,
            center_y + speaker_height // 2
        ],
        fill=accent_color
    )
    
    # Конус динамика (треугольник)
    draw.polygon(
        [
            (center_x - size // 8, center_y - speaker_height // 2),
            (center_x + size // 6, center_y - size // 3),
            (center_x + size // 6, center_y + size // 3),
            (center_x - size // 8, center_y + speaker_height // 2)
        ],
        fill=accent_color
    )
    
    # Звуковые волны
    wave_start = center_x + size // 5
    
    # Первая волна (маленькая)
    draw.arc(
        [wave_start, center_y - size // 6, wave_start + size // 8, center_y + size // 6],
        start=-60, end=60,
        fill=light_color, width=3
    )
    
    # Вторая волна (средняя)
    draw.arc(
        [wave_start + size // 12, center_y - size // 4, wave_start + size // 4, center_y + size // 4],
        start=-60, end=60,
        fill=light_color, width=3
    )
    
    # Третья волна (большая)
    draw.arc(
        [wave_start + size // 6, center_y - size // 3, wave_start + size // 3 + 2, center_y + size // 3],
        start=-60, end=60,
        fill=light_color, width=3
    )
    
    return img


def get_icon_bytes():
    """Возвращает иконку в виде байтов PNG"""
    img = create_icon_image(64)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def get_icon_base64():
    """Возвращает иконку в формате base64"""
    return base64.b64encode(get_icon_bytes()).decode('utf-8')


# Для обратной совместимости - создаём ICON как байты
def get_icon():
    """Возвращает объект Image иконки"""
    return create_icon_image(64)


# ICON теперь генерируется динамически
ICON = None  # Будет None, используйте get_icon() или get_icon_bytes()
