<div align="center">
  <img src="app/logo.png" alt="x2 UpScale Logo" width="192" height="192">
  <h1>🚀 x2 UpScale</h1>
  <p>
    <a href="README.md">🏠 Главная</a> •
    <a href="README.ua.md">🇺🇦</a> •
    <a href="README.en.md">🇬🇧</a>
  </p>
  <br>
</div>

# 🇷🇺 x2 UpScale — Русский

**x2 UpScale** — программа для увеличения изображений в 2×–4× с помощью ИИ.

Работает на **Real-ESRGAN ncnn (Vulkan)** — не требует CUDA/PyTorch, подходит для любого GPU.  
Фотореалистичный режим через **Real-ESRGAN x4plus (CUDA)** — опционально.

---

## ✨ Возможности

| Возможность | Описание |
|-------------|---------|
| 🎨 **Анимация / Claymation** | ncnn Vulkan — встроен, работает сразу на любом GPU |
| 📷 **Фотореализм** | PyTorch CUDA — опционально, ставится отдельно |
| 🖥️ **Графический интерфейс** | PyQt6, тёмная тема Fusion |
| ⌨️ **CLI** | Полноценный консольный режим |
| 🌍 **Мультиязычность** | 🇷🇺 🇺🇦 🇬🇧 — переключение флагами |
| 🔄 **Batch обработка** | Папка целиком |
| 🧩 **Tiling** | Обработка больших изображений по тайлам |
| 🎚️ **Scale 1×–4×** | Плавный слайдер + пресеты |

---

## 🚀 Быстрый старт

```bash
# 1️⃣ Установить Python 3.10+ (https://python.org/downloads)
# 2️⃣ Установить зависимости
pip install -r requirements.txt

# 3️⃣ Запустить GUI
python main.py

# Или CLI:
python main.py photo.jpg --out result.png
```

### 📦 Для фоторежима (опционально)

```bash
pip install -r requirements-photo.txt
```
Модель `RealESRGAN_x4plus.pth` (67 МБ) скачается автоматически при первом переключении на фоторежим.

---

## 🖥️ Интерфейс

### GUI

![x2 UpScale GUI](app/screenshot.png)

```bash
python main.py
```

### CLI

```bash
# Одиночный файл
python main.py image.jpg -o result.png

# Batch: папка → папка
python main.py input_folder/ --out output_folder/

# Список доступных backend-ов
python main.py --list-methods
```

---

## 🧠 Backends (модели)

| Модель | Движок | Тип | Требования |
|--------|--------|-----|-----------|
| 🔮 **AnimeVideoV3** | ncnn Vulkan | Анимация / Claymation | Любой GPU с Vulkan (встроен) |
| 📷 **RealESRGAN x4plus** | PyTorch CUDA | Фотореализм | NVIDIA + `requirements-photo.txt` |

**AnimeVideoV3** — основной режим. Работает сразу после установки, не требует дополнительных пакетов.  
**RealESRGAN x4plus** — для фотографий. Требует установки PyTorch + realesrgan.

---

## 🏗️ Структура проекта

```
x2-upscale/
├── main.py                    # Точка входа
├── install.bat                # Установщик для Windows
├── requirements.txt           # Базовые зависимости (Pillow, PyQt6)
├── requirements-photo.txt     # Для фоторежима (torch, realesrgan)
├── bin/ncnn/                  # Real-ESRGAN ncnn Vulkan (встроен)
│   ├── realesrgan-ncnn-vulkan.exe
│   ├── vcomp140.dll
│   └── models/realesr-animevideov3-x2.*
├── app/
│   ├── gui/app.py             # PyQt6 GUI
│   ├── models/                # Бэкенды upscale
│   ├── core.py                # Оркестратор
│   └── logo.png               # Логотип
└── models/realesrgan/         # Сюда скачивается x4plus.pth
```

---

## 📋 Системные требования

- **Python 3.10+**
- **GPU с Vulkan** — для ncnn (NVIDIA, AMD, Intel — любой)
- **NVIDIA GPU + CUDA** — для фоторежима (опционально)

---

## 🏆 Благодарности (Credits)

Этот проект использует следующие Open Source компоненты:

| Проект | Автор | Описание |
|--------|-------|---------|
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | [Xintao Wang](https://github.com/xinntao) | Основной алгоритм AI upscale |
| [ncnn Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan) | [Xintao Wang](https://github.com/xinntao) | Vulkan бинарник (ncnn) |
| [PyTorch](https://pytorch.org) | Meta | Фреймворк для фоторежима |
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) | Riverbank Computing | GUI |
| [Pillow](https://python-pillow.org) | — | Обработка изображений |

**Сделано с ❤️ [Mr3ster](https://github.com/ZetHor3)**

---

<br>

<div align="center">
  <sub>© 2026 <a href="https://github.com/ZetHor3">Mr3ster</a> | Powered by <a href="https://github.com/xinntao/Real-ESRGAN">Real-ESRGAN</a></sub>
  <br>
  <sub><a href="https://boosty.to/mr3ster/donate">💜 Support Us</a></sub>
</div>
