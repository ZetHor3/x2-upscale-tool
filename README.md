# x2 UpScale

Image upscaling tool with **GUI** and **CLI** interfaces.  
Real-ESRGAN AI upscaling via Vulkan (любой GPU) или CUDA.

## Быстрый старт

```bash
# 1. Установить базовые зависимости
pip install -r requirements.txt

# 2. Запустить GUI
python main.py

# 3. Или CLI:
python main.py photo.jpg --out result.png
```

## Установка (для пользователей)

1. Установи **Python 3.10+** (https://www.python.org/downloads/)
2. Запусти `install.bat` — он сам всё поставит
3. Запускай `python main.py`

Всё остальное (Real-ESRGAN ncnn Vulkan бинарник + модель) уже встроено в проект.

### Если нужен фотореализм (Real-ESRGAN x4plus CUDA)

```bash
pip install -r requirements-photo.txt
```
Модель скачается автоматически при первом переключении на фоторежим.

## Интерфейс

**GUI (по умолчанию):**
```bash
python main.py
```

**CLI:**
```bash
# Базовый 2x upscale
python main.py photo.jpg -o result.png

# Batch папка → папка
python main.py input_folder/ --out output_folder/

# CLI со списком методов
python main.py --list-methods
```

## Backends (выбор модели в GUI)

| Модель | Движок | Для чего |
|--------|--------|----------|
| 🔮 AnimeVideoV3 | ncnn Vulkan | **Анимация, claymation** (встроен, работает сразу) |
| 📷 RealESRGAN x4plus | PyTorch CUDA | **Фотореализм** (нужен `requirements-photo.txt`) |

**AnimeVideoV3** — основной режим. Не требует CUDA/PyTorch, работает на любом GPU через Vulkan.
Встроен прямо в проект (`bin/ncnn/`).

## Структура проекта

```
x2-upscale/
├── main.py              # Точка входа
├── install.bat          # Установщик для Windows
├── requirements.txt     # Базовые зависимости (Pillow, PyQt6)
├── requirements-photo.txt  # Для фоторежима (torch, realesrgan)
├── bin/ncnn/            # Встроенный Real-ESRGAN ncnn Vulkan
│   ├── realesrgan-ncnn-vulkan.exe
│   └── models/          # animevideov3-x2 модель
├── app/
│   ├── gui/app.py       # PyQt6 GUI
│   ├── models/          # Бэкенды upscale
│   └── core.py          # Оркестратор
└── models/realesrgan/   # Сюда авто-скачивается x4plus.pth
```

## Системные требования

- **Python 3.10+**
- **GPU с Vulkan** — для ncnn (любой: NVIDIA, AMD, Intel)
- **NVIDIA GPU + CUDA** — для фоторежима (опционально)
