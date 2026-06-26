"""Internationalisation — RU / UK / EN with persistent config."""

import json
import os
from pathlib import Path


CONFIG_DIR = Path(os.environ.get("APPDATA", "~")) / "x2-upscale"
CONFIG_FILE = CONFIG_DIR / "config.json"

LANG_CODES = ["ru", "uk", "en"]

LANG_FLAGS = {
    "ru": "🇷🇺",
    "uk": "🇺🇦",
    "en": "🇺🇸",
}

LANG_LABELS = {
    "ru": "Русский",
    "uk": "Українська",
    "en": "English",
}

# ── Translation table ────────────────────────────────────────────

T = {
    "ru": {
        "app_title": "x2 UpScale",
        "settings": "Настройки",
        "input_files": "Входные файлы",
        "no_files": "Файлы не выбраны",
        "add_files": "Добавить файлы",
        "add_folder": "Добавить папку",
        "clear": "Очистить",
        "drag_hint": "Перетащите изображения сюда\nили используйте кнопки выше",
        "files_selected": "файлов выбрано",
        "method": "Метод апскейла",
        "scale": "Масштаб",
        "options": "Опции",
        "output": "Вывод",
        "output_dir_hint": "Та же папка, что и исходники",
        "browse": "Обзор",
        "suffix": "Суффикс",
        "file_list": "Файлы",
        "log": "Лог",
        "status_ready": "Готов",
        "status_processing": "Обработка...",
        "status_done": "Готово",
        "run": "▶ Апскейл",
        "stop": "■ Стоп",
        "open_output": "Открыть папку",
        "powered_by": "Powered by",
        "support_us": "Support Us",
        "starting": "Запуск апскейла...",
        "stopping": "Остановка (завершится текущий файл)...",
        "done_ok": "OK",
        "done_failed": "ошибок",
        "error": "Ошибка",
        "no_files_warn": "Нет файлов",
        "no_files_msg": "Сначала добавьте изображения.",
        "no_output_msg": "Выберите папку для сохранения результата.",
        "error_title": "Ошибка",
        "filter_images": "Изображения (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif *.avif)",
        "all_files": "Все файлы (*.*)",
        "select_images": "Выберите изображения",
        "select_folder": "Выберите папку с изображениями",
        "select_output": "Выберите папку для результатов",
        "scale_preset": "×",
        "sharpness": "Резкость",
        "filter": "Фильтр",
        "model": "Модель",
    },
    "uk": {
        "app_title": "x2 UpScale",
        "settings": "Налаштування",
        "input_files": "Вхідні файли",
        "no_files": "Файли не вибрано",
        "add_files": "Додати файли",
        "add_folder": "Додати папку",
        "clear": "Очистити",
        "drag_hint": "Перетягніть зображення сюди\nабо використайте кнопки вище",
        "files_selected": "файлів вибрано",
        "method": "Метод апскейлу",
        "scale": "Масштаб",
        "options": "Опції",
        "output": "Вивід",
        "output_dir_hint": "Та ж папка, що й джерела",
        "browse": "Огляд",
        "suffix": "Суфікс",
        "file_list": "Файли",
        "log": "Лог",
        "status_ready": "Готов",
        "status_processing": "Обробка...",
        "status_done": "Готово",
        "run": "▶ Апскейл",
        "stop": "■ Стоп",
        "open_output": "Відкрити папку",
        "powered_by": "Powered by",
        "support_us": "Support Us",
        "starting": "Запуск апскейлу...",
        "stopping": "Зупинка (завершиться поточний файл)...",
        "done_ok": "ОК",
        "done_failed": "помилок",
        "error": "Помилка",
        "no_files_warn": "Немає файлів",
        "no_files_msg": "Спочатку додайте зображення.",
        "no_output_msg": "Виберіть папку для збереження результату.",
        "error_title": "Помилка",
        "filter_images": "Зображення (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif *.avif)",
        "all_files": "Усі файли (*.*)",
        "select_images": "Виберіть зображення",
        "select_folder": "Виберіть папку із зображеннями",
        "select_output": "Виберіть папку для результатів",
        "scale_preset": "×",
        "sharpness": "Різкість",
        "filter": "Фільтр",
        "model": "Модель",
    },
    "en": {
        "app_title": "x2 UpScale",
        "settings": "Settings",
        "input_files": "Input Files",
        "no_files": "No files selected",
        "add_files": "Add Files",
        "add_folder": "Add Folder",
        "clear": "Clear",
        "drag_hint": "Drag & drop images here\nor use the buttons above",
        "files_selected": "file(s) selected",
        "method": "Upscaling Method",
        "scale": "Scale",
        "options": "Options",
        "output": "Output",
        "output_dir_hint": "Same as input folder",
        "browse": "Browse",
        "suffix": "Suffix",
        "file_list": "Files",
        "log": "Log",
        "status_ready": "Ready",
        "status_processing": "Processing...",
        "status_done": "Done",
        "run": "▶ Upscale",
        "stop": "■ Stop",
        "open_output": "Open Output",
        "powered_by": "Powered by",
        "support_us": "Support Us",
        "starting": "Starting upscale...",
        "stopping": "Stopping (will finish current file)...",
        "done_ok": "OK",
        "done_failed": "failed",
        "error": "Error",
        "no_files_warn": "No files",
        "no_files_msg": "Add image files first.",
        "no_output_msg": "Select an output folder for results.",
        "error_title": "Error",
        "filter_images": "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif *.avif)",
        "all_files": "All files (*.*)",
        "select_images": "Select Images",
        "select_folder": "Select Folder with Images",
        "select_output": "Select Output Folder",
        "scale_preset": "×",
        "sharpness": "Sharpness",
        "filter": "Filter",
        "model": "Model",
    },
}


class Language:
    """Singleton-ish language manager with persistent config."""

    _current = "ru"

    @classmethod
    def load(cls) -> str:
        """Load saved language from config, default 'ru'."""
        try:
            if CONFIG_FILE.exists():
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                lang = data.get("language", "ru")
                if lang in LANG_CODES:
                    cls._current = lang
                    return lang
        except Exception:
            pass
        cls._current = "ru"
        return "ru"

    @classmethod
    def save(cls, lang: str) -> None:
        """Persist language choice."""
        if lang not in LANG_CODES:
            return
        cls._current = lang
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            data = {}
            if CONFIG_FILE.exists():
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            data["language"] = lang
            CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def current(cls) -> str:
        return cls._current

    @classmethod
    def tr(cls, key: str) -> str:
        """Translate a key into the current language."""
        return T.get(cls._current, T["ru"]).get(key, key)


# Initial load
Language.load()


def tr(key: str) -> str:
    """Shortcut."""
    return Language.tr(key)
