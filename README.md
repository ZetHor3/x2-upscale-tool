<div align="center">
  <img src="app/logo.png" alt="x2 UpScale Logo" width="192" height="192">
  <h1>🚀 x2 UpScale</h1>
  <p><b>Image upscaling tool with AI — GUI + CLI</b></p>
  <p>
    <a href="#🇷🇺-русский">🇷🇺</a> •
    <a href="#🇺🇦-українська">🇺🇦</a> •
    <a href="#🇬🇧-english">🇬🇧</a>
  </p>
  <br>
</div>

---

<a name="🇷🇺-русский"></a>
# 🇷🇺 Русский

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

![GUI Preview](app/logo.png)

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

<a name="🇺🇦-українська"></a>
# 🇺🇦 Українська

**x2 UpScale** — програма для збільшення зображень у 2×–4× за допомогою ШІ.

Працює на **Real-ESRGAN ncnn (Vulkan)** — не потребує CUDA/PyTorch, підходить для будь-якого GPU.  
Фотореалістичний режим через **Real-ESRGAN x4plus (CUDA)** — опціонально.

---

## ✨ Можливості

| Можливість | Опис |
|-------------|---------|
| 🎨 **Анімація / Claymation** | ncnn Vulkan — вбудовано, працює одразу на будь-якому GPU |
| 📷 **Фотореалізм** | PyTorch CUDA — опціонально |
| 🖥️ **Графічний інтерфейс** | PyQt6, темна тема Fusion |
| ⌨️ **CLI** | Повноцінний консольний режим |
| 🌍 **Багатомовність** | 🇷🇺 🇺🇦 🇬🇧 — перемикання прапорцями |
| 🔄 **Batch обробка** | Ціла папка |
| 🧩 **Tiling** | Обробка великих зображень по тайлах |
| 🎚️ **Scale 1×–4×** | Плавний слайдер + пресети |

---

## 🚀 Швидкий старт

```bash
# 1️⃣ Встановити Python 3.10+ (https://python.org/downloads)
# 2️⃣ Встановити залежності
pip install -r requirements.txt

# 3️⃣ Запустити GUI
python main.py

# Або CLI:
python main.py photo.jpg --out result.png
```

### 📦 Для фоторежиму (опціонально)

```bash
pip install -r requirements-photo.txt
```
Модель `RealESRGAN_x4plus.pth` (67 МБ) завантажиться автоматично при першому перемиканні на фоторежим.

---

## 🖥️ Інтерфейс

### GUI

```bash
python main.py
```

### CLI

```bash
python main.py image.jpg -o result.png
python main.py input_folder/ --out output_folder/
python main.py --list-methods
```

---

## 🧠 Backends (моделі)

| Модель | Движок | Тип | Вимоги |
|--------|--------|-----|--------|
| 🔮 **AnimeVideoV3** | ncnn Vulkan | Анімація / Claymation | Будь-який GPU з Vulkan (вбудовано) |
| 📷 **RealESRGAN x4plus** | PyTorch CUDA | Фотореалізм | NVIDIA + `requirements-photo.txt` |

---

## 🏆 Подяки (Credits)

| Проєкт | Автор |
|--------|-------|
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | [Xintao Wang](https://github.com/xinntao) |
| [ncnn Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan) | [Xintao Wang](https://github.com/xinntao) |
| [PyTorch](https://pytorch.org) | Meta |
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) | Riverbank Computing |
| [Pillow](https://python-pillow.org) | — |

**Зроблено з ❤️ [Mr3ster](https://github.com/ZetHor3)**

---

<br>

<a name="🇬🇧-english"></a>
# 🇬🇧 English

**x2 UpScale** — AI-powered image upscaling tool with GUI and CLI.

Powered by **Real-ESRGAN ncnn (Vulkan)** — works on any GPU, no CUDA required.  
Optional **Real-ESRGAN x4plus (CUDA)** for photorealism.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎨 **Animation / Claymation** | ncnn Vulkan — built-in, works out of the box |
| 📷 **Photorealism** | PyTorch CUDA — optional |
| 🖥️ **Graphical Interface** | PyQt6, dark Fusion theme |
| ⌨️ **CLI** | Full command-line mode |
| 🌍 **Multilingual** | 🇷🇺 🇺🇦 🇬🇧 — switch via flags |
| 🔄 **Batch Processing** | Process entire folders |
| 🧩 **Tiling** | Large image support via tiles |
| 🎚️ **Scale 1×–4×** | Smooth slider + presets |

---

## 🚀 Quick Start

```bash
# 1️⃣ Install Python 3.10+ (https://python.org/downloads)
# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Launch GUI
python main.py

# Or CLI:
python main.py photo.jpg --out result.png
```

### 📦 Photo mode (optional)

```bash
pip install -r requirements-photo.txt
```
The `RealESRGAN_x4plus.pth` (67 MB) model will auto-download on first use.

---

## 🖥️ Interface

### GUI

```bash
python main.py
```

### CLI

```bash
python main.py image.jpg -o result.png
python main.py input_folder/ --out output_folder/
python main.py --list-methods
```

---

## 🧠 Backends

| Model | Engine | Type | Requirements |
|-------|--------|------|-------------|
| 🔮 **AnimeVideoV3** | ncnn Vulkan | Animation / Claymation | Any Vulkan GPU (built-in) |
| 📷 **RealESRGAN x4plus** | PyTorch CUDA | Photorealism | NVIDIA + `requirements-photo.txt` |

---

## 🏆 Credits

| Project | Author |
|---------|--------|
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | [Xintao Wang](https://github.com/xinntao) |
| [ncnn Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan) | [Xintao Wang](https://github.com/xinntao) |
| [PyTorch](https://pytorch.org) | Meta |
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) | Riverbank Computing |
| [Pillow](https://python-pillow.org) | — |

**Made with ❤️ by [Mr3ster](https://github.com/ZetHor3)**

---

<br>

<div align="center">
  <sub>© 2026 <a href="https://github.com/ZetHor3">Mr3ster</a> | Powered by <a href="https://github.com/xinntao/Real-ESRGAN">Real-ESRGAN</a></sub>
  <br>
  <sub><a href="https://boosty.to/mr3ster/donate">💜 Support Us</a></sub>
</div>
