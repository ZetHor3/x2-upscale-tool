"""Main GUI application — PyQt6-based upscaling UI with i18n and branding."""

import os
import sys
import threading
from pathlib import Path

from PyQt6.QtCore import (
    Qt, QRect, QSize, QUrl, pyqtSignal, QObject, QThread,
)
from PyQt6.QtGui import (
    QAction, QColor, QFont, QIcon, QPainter, QPalette, QPixmap,
    QDesktopServices, QTextCursor,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSlider, QProgressBar,
    QTextEdit, QListWidget, QScrollArea, QFrame, QSplitter,
    QFileDialog, QMessageBox, QSizePolicy, QButtonGroup,
)

from ..core import UpscaleEngine, UpscaleJob
from .. import models
from .. import utils
from .i18n import Language, tr, LANG_CODES, LANG_FLAGS


# ── Styling ──────────────────────────────────────────────────────

APP_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", "Arial", sans-serif;
}
QLabel {
    color: #e0e0e0;
    background: transparent;
}
QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#sectionTitle {
    font-size: 13px;
    font-weight: bold;
    color: #bb86fc;
    padding: 4px 0 2px 0;
}
QLabel#logEntry {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    color: #c0c0c0;
}
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px 14px;
    color: #e0e0e0;
    font-size: 12px;
    min-height: 18px;
}
QPushButton:hover {
    background-color: #3a3a3a;
    border-color: #bb86fc;
}
QPushButton:pressed {
    background-color: #4a4a4a;
}
QPushButton:disabled {
    background-color: #252525;
    color: #666;
    border-color: #333;
}
QPushButton#runBtn {
    background-color: #2e7d32;
    border-color: #388e3c;
    font-weight: bold;
    min-width: 120px;
}
QPushButton#runBtn:hover {
    background-color: #388e3c;
}
QPushButton#runBtn:disabled {
    background-color: #1b3a1d;
    border-color: #2a5a2c;
    color: #666;
}
QPushButton#stopBtn {
    background-color: #8b1a1a;
    border-color: #a02020;
    font-weight: bold;
    min-width: 80px;
}
QPushButton#stopBtn:hover {
    background-color: #a02020;
}
QPushButton#stopBtn:disabled {
    background-color: #3a1a1a;
    border-color: #4a2a2a;
    color: #666;
}
QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
    font-size: 12px;
    min-height: 18px;
}
QComboBox:hover {
    border-color: #bb86fc;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #3c3c3c;
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    color: #e0e0e0;
    selection-background-color: #3a3a3a;
}
QSlider::groove:horizontal {
    background: #3c3c3c;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #bb86fc;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #bb86fc;
    border-radius: 2px;
}
QTextEdit, QListWidget {
    background-color: #121212;
    border: 1px solid #333;
    border-radius: 4px;
    color: #c0c0c0;
    font-size: 11px;
}
QTextEdit {
    font-family: "Consolas", "Courier New", monospace;
}
QListWidget::item {
    padding: 2px 4px;
    border-bottom: 1px solid #252525;
}
QListWidget::item:selected {
    background-color: #3a3a3a;
    color: #bb86fc;
}
QScrollBar:vertical {
    background: #1e1e1e;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #3c3c3c;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #555;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QProgressBar {
    background-color: #252525;
    border: 1px solid #333;
    border-radius: 4px;
    text-align: center;
    font-size: 10px;
    color: #bbb;
    height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c4dff, stop:0.5 #bb86fc, stop:1 #7c4dff);
    border-radius: 3px;
}
QFrame#bottomBar {
    background-color: #1a1a2e;
    border-top: 1px solid #333;
    border-radius: 0;
    padding: 6px 12px;
}
QFrame#sectionFrame {
    background-color: #252525;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 10px;
}
QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
    font-size: 12px;
}
QLineEdit:hover {
    border-color: #bb86fc;
}
"""


# ── Flag painting ────────────────────────────────────────────────

def _paint_flag_ru(painter: QPainter, rect, size) -> None:
    """White / Blue / Red horizontal stripes."""
    h3 = rect.height() / 3
    painter.fillRect(QRect(rect.x(), rect.y(), rect.width(), int(h3)), Qt.GlobalColor.white)
    painter.fillRect(QRect(rect.x(), rect.y() + int(h3), rect.width(), int(h3)), QColor("#0039a6"))
    painter.fillRect(QRect(rect.x(), rect.y() + int(h3 * 2), rect.width(), int(h3 + 0.5)), QColor("#d52b1e"))


def _paint_flag_ua(painter: QPainter, rect, size) -> None:
    """Blue / Yellow horizontal stripes."""
    h2 = rect.height() / 2
    painter.fillRect(QRect(rect.x(), rect.y(), rect.width(), int(h2)), QColor("#005bbb"))
    painter.fillRect(QRect(rect.x(), rect.y() + int(h2), rect.width(), int(h2 + 0.5)), QColor("#ffd500"))


def _paint_flag_us(painter: QPainter, rect, size) -> None:
    """Stripes + blue canton."""
    w, h = rect.width(), rect.height()
    stripe_h = h / 13
    # Stripes
    for i in range(13):
        color = QColor("#b22234") if i % 2 == 0 else Qt.GlobalColor.white
        painter.fillRect(QRect(rect.x(), rect.y() + int(i * stripe_h), w, int(stripe_h + 0.5)), color)
    # Canton
    canton_w = int(w * 0.4)
    canton_h = int(h * 0.538)
    painter.fillRect(QRect(rect.x(), rect.y(), canton_w, canton_h), QColor("#3c3b6e"))


FLAG_PAINTERS = {
    "ru": _paint_flag_ru,
    "uk": _paint_flag_ua,
    "en": _paint_flag_us,
}


class FlagButton(QPushButton):
    """Small clickable flag button."""

    def __init__(self, lang_code: str, parent=None):
        super().__init__(parent)
        self._lang = lang_code
        self._paint = FLAG_PAINTERS[lang_code]
        self.setFixedSize(36, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{LANG_FLAGS[lang_code]} {lang_code.upper()}")
        self.setCheckable(True)
        style = """
            QPushButton {
                background: transparent;
                border: 2px solid transparent;
                border-radius: 2px;
            }
            QPushButton:checked {
                border: 2px solid #bb86fc;
            }
            QPushButton:hover {
                border: 2px solid #888;
            }
        """
        self.setStyleSheet(style)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        r = self.rect().adjusted(2, 2, -2, -2)
        # Clip to rounded rect
        painter.save()
        path = _rounded_rect_path(r, 2)
        painter.setClipPath(path)
        self._paint(painter, r, self.size())
        painter.restore()
        # Border
        painter.setPen(QColor("#555"))
        painter.drawRoundedRect(r, 2, 2)


def _rounded_rect_path(rect, radius):
    from PyQt6.QtCore import QRectF
    from PyQt6.QtGui import QPainterPath
    path = QPainterPath()
    path.addRoundedRect(QRectF(rect), radius, radius)
    return path


# ── Background worker for upscaling ─────────────────────────────

class UpscaleSignals(QObject):
    progress = pyqtSignal(int, int, object)  # completed, total, job
    finished = pyqtSignal(list)              # list[UpscaleJob]


class UpscaleWorker(QObject):
    """Runs upscale jobs in a background thread."""

    def __init__(self, engine: UpscaleEngine, jobs: list[UpscaleJob]):
        super().__init__()
        self.engine = engine
        self.jobs = jobs
        self.signals = UpscaleSignals()
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        results = []
        for i, job in enumerate(self.jobs):
            if self._stop_flag:
                break
            self.engine.upscale_one(job)
            results.append(job)
            self.signals.progress.emit(i + 1, len(self.jobs), job)
        self.signals.finished.emit(results)

    @property
    def progress_signal(self):
        return self.signals.progress

    @property
    def finished_signal(self):
        return self.signals.finished


# ── Main Window ──────────────────────────────────────────────────

class UpscaleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self._engine: UpscaleEngine | None = None
        self._worker: UpscaleWorker | None = None
        self._thread: QThread | None = None
        self._file_list: list[Path] = []
        self._current_results: list[UpscaleJob] = []
        self._option_widgets: dict = {}

        self._build_ui()
        self._rebuild_engine()
        self._apply_language()

        Language.load()
        current_lang = Language.current()
        self._set_language(current_lang)

    # ── UI Build ──────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("x2 UpScale")
        self.setMinimumSize(880, 620)
        self.resize(1020, 720)

        # Set window icon
        logo_path = Path(__file__).parent.parent.parent / "app" / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 8, 12, 0)
        main_layout.setSpacing(6)

        # ── Title ──
        title = QLabel("x2 UpScale")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # ── Splitter: left settings + right files/log ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, stretch=1)

        # Left panel (scrollable settings)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        left_panel = QWidget()
        self._left_layout = QVBoxLayout(left_panel)
        self._left_layout.setContentsMargins(0, 0, 4, 0)
        self._left_layout.setSpacing(8)

        self._build_input_section()
        self._build_method_section()
        self._build_scale_section()
        self._build_options_section()
        self._build_output_section()

        self._left_layout.addStretch()
        scroll.setWidget(left_panel)
        splitter.addWidget(scroll)

        # Right panel: file list + log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(4)

        self._file_list_label = QLabel()
        self._file_list_label.setObjectName("sectionTitle")
        right_layout.addWidget(self._file_list_label)

        self._file_widget = QListWidget()
        self._file_widget.setAlternatingRowColors(False)
        right_layout.addWidget(self._file_widget, stretch=2)

        self._log_label = QLabel()
        self._log_label.setObjectName("sectionTitle")
        right_layout.addWidget(self._log_label)

        self._log_widget = QTextEdit()
        self._log_widget.setReadOnly(True)
        self._log_widget.setObjectName("logEntry")
        right_layout.addWidget(self._log_widget, stretch=1)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 520])

        # ── Progress bar ──
        self._progress_bar = QProgressBar()
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setValue(0)
        main_layout.addWidget(self._progress_bar)

        # ── Bottom bar: Powered by + Flags + Support Us ──
        bottom = QFrame()
        bottom.setObjectName("bottomBar")
        bottom.setFixedHeight(36)
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(8, 2, 8, 2)
        bottom_layout.setSpacing(6)

        # "Powered by Mr3ster" (Mr3ster — clickable link)
        powered_label = QLabel()
        powered_label.setObjectName("poweredLabel")
        powered_label.setStyleSheet("color: #888; font-size: 11px; background: transparent;")
        powered_label.setOpenExternalLinks(True)
        powered_label.setText(
            f'{tr("powered_by")} '
            f'<a href="https://github.com/ZetHor3" '
            f'style="color: #bb86fc; text-decoration: none;">Mr3ster</a>'
        )
        bottom_layout.addWidget(powered_label)

        # Flags group
        self._flag_group = QButtonGroup(self)
        self._flag_group.setExclusive(True)
        self._flag_buttons = {}
        for code in LANG_CODES:
            btn = FlagButton(code)
            self._flag_group.addButton(btn)
            self._flag_buttons[code] = btn
            bottom_layout.addWidget(btn)
        self._flag_group.buttonClicked.connect(self._on_flag_clicked)

        bottom_layout.addStretch()

        # Support Us
        support_label = QLabel()
        support_label.setObjectName("supportLabel")
        support_label.setStyleSheet(
            "color: #bb86fc; font-size: 11px; font-weight: bold; background: transparent;"
            " text-decoration: underline;"
        )
        support_label.setCursor(Qt.CursorShape.PointingHandCursor)
        support_label.mousePressEvent = lambda e: QDesktopServices.openUrl(
            QUrl("https://boosty.to/mr3ster/donate")
        )
        bottom_layout.addWidget(support_label)

        main_layout.addWidget(bottom)

        # ── Status row: status + buttons ──
        status_row = QWidget()
        status_row.setStyleSheet("background: transparent;")
        status_layout = QHBoxLayout(status_row)
        status_layout.setContentsMargins(0, 2, 0, 4)

        self._status_label = QLabel()
        self._status_label.setStyleSheet("color: #aaa; font-size: 11px; background: transparent;")
        status_layout.addWidget(self._status_label)

        status_layout.addStretch()

        self._run_btn = QPushButton()
        self._run_btn.setObjectName("runBtn")
        self._run_btn.clicked.connect(self._run_upscale)
        status_layout.addWidget(self._run_btn)

        self._stop_btn = QPushButton()
        self._stop_btn.setObjectName("stopBtn")
        self._stop_btn.clicked.connect(self._stop_upscale)
        self._stop_btn.setEnabled(False)
        status_layout.addWidget(self._stop_btn)

        self._open_btn = QPushButton()
        self._open_btn.setObjectName("openBtn")
        self._open_btn.clicked.connect(self._open_output)
        status_layout.addWidget(self._open_btn)

        main_layout.addWidget(status_row)

    def _build_input_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        self._input_title = QLabel()
        self._input_title.setObjectName("sectionTitle")
        layout.addWidget(self._input_title)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        self._file_count_label = QLabel()
        self._file_count_label.setStyleSheet("color: #888; font-size: 11px; background: transparent;")
        btn_row.addWidget(self._file_count_label, stretch=1)

        self._add_files_btn = QPushButton()
        self._add_files_btn.clicked.connect(self._add_files)
        btn_row.addWidget(self._add_files_btn)

        self._add_folder_btn = QPushButton()
        self._add_folder_btn.clicked.connect(self._add_folder)
        btn_row.addWidget(self._add_folder_btn)

        self._clear_btn = QPushButton()
        self._clear_btn.clicked.connect(self._clear_files)
        btn_row.addWidget(self._clear_btn)

        layout.addLayout(btn_row)
        self._left_layout.addWidget(frame)

    def _build_method_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        self._method_title = QLabel()
        self._method_title.setObjectName("sectionTitle")
        layout.addWidget(self._method_title)

        # Fixed backend: Real-ESRGAN ncnn (Vulkan)
        method_label = QLabel("🔷 Real-ESRGAN ncnn (Vulkan)")
        method_label.setStyleSheet(
            "color: #bb86fc; font-size: 13px; font-weight: bold; background: transparent; "
            "padding: 6px 8px; border: 1px solid #bb86fc; border-radius: 4px;"
        )
        layout.addWidget(method_label)

        # Model selector
        model_row = QHBoxLayout()
        model_label_ = QLabel("🎨 Модель:")
        model_label_.setStyleSheet("color: #ccc; font-size: 11px; background: transparent;")
        model_row.addWidget(model_label_)

        self._model_combo = QComboBox()
        self._model_combo.addItem("🔮 AnimeVideoV3 (claymation/animation)", "ncnn:realesr-animevideov3")
        self._model_combo.addItem("📷 RealESRGAN x4plus (фотореализм)", "py:RealESRGAN_x4plus.pth")
        self._model_combo.setStyleSheet("""
            QComboBox { background: #2d2d2d; border: 1px solid #3c3c3c;
                border-radius: 4px; padding: 4px 8px; color: #e0e0e0;
                font-size: 11px; min-height: 16px; }
            QComboBox:hover { border-color: #bb86fc; }
            QComboBox::drop-down { width: 20px; }
        """)
        self._model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_row.addWidget(self._model_combo, stretch=1)
        layout.addLayout(model_row)

        self._ai_status_label = QLabel()
        self._ai_status_label.setStyleSheet(
            "color: #4caf50; font-size: 10px; background: transparent; padding: 2px 0;"
        )
        self._ai_status_label.setWordWrap(True)
        layout.addWidget(self._ai_status_label)

        self._left_layout.addWidget(frame)
        # Engine always ncnn
        self._rebuild_engine("ncnn")

    def _build_scale_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        self._scale_title = QLabel()
        self._scale_title.setObjectName("sectionTitle")
        layout.addWidget(self._scale_title)

        slider_row = QHBoxLayout()
        self._scale_slider = QSlider(Qt.Orientation.Horizontal)
        self._scale_slider.setRange(10, 40)  # 1.0 – 4.0
        self._scale_slider.setValue(20)       # 2.0
        self._scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._scale_slider.setTickInterval(5)
        self._scale_slider.valueChanged.connect(self._on_scale_changed)
        slider_row.addWidget(self._scale_slider, stretch=1)

        self._scale_value_label = QLabel("2.0×")
        self._scale_value_label.setFixedWidth(40)
        self._scale_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scale_value_label.setStyleSheet("color: #bb86fc; font-weight: bold; font-size: 13px; background: transparent;")
        slider_row.addWidget(self._scale_value_label)

        layout.addLayout(slider_row)

        # Preset buttons
        preset_row = QHBoxLayout()
        preset_row.setSpacing(4)
        for val in [1.5, 2.0, 3.0, 4.0]:
            btn = QPushButton(f"{val}×")
            btn.setFixedSize(42, 24)
            btn.setStyleSheet("font-size: 10px; padding: 2px 6px;")
            btn.clicked.connect(lambda _, v=val: self._set_scale(v))
            preset_row.addWidget(btn)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        self._left_layout.addWidget(frame)

    def _build_options_section(self):
        self._options_frame = QFrame()
        self._options_frame.setObjectName("sectionFrame")
        self._options_layout = QVBoxLayout(self._options_frame)
        self._options_layout.setContentsMargins(8, 6, 8, 6)
        self._options_layout.setSpacing(4)

        self._options_title = QLabel()
        self._options_title.setObjectName("sectionTitle")
        self._options_layout.addWidget(self._options_title)

        # Container for dynamic options
        self._options_container = QWidget()
        self._options_container.setStyleSheet("background: transparent;")
        self._options_container_layout = QVBoxLayout(self._options_container)
        self._options_container_layout.setContentsMargins(0, 0, 0, 0)
        self._options_container_layout.setSpacing(4)
        self._options_layout.addWidget(self._options_container)

        self._left_layout.addWidget(self._options_frame)

    def _build_output_section(self):
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        self._output_frame = frame
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        self._output_title = QLabel()
        self._output_title.setObjectName("sectionTitle")
        layout.addWidget(self._output_title)

        dir_row = QHBoxLayout()
        self._output_dir_label = QLabel()
        self._output_dir_label.setStyleSheet("color: #888; font-size: 11px; background: transparent;")
        dir_row.addWidget(self._output_dir_label, stretch=1)

        self._browse_btn = QPushButton()
        self._browse_btn.clicked.connect(self._browse_output)
        dir_row.addWidget(self._browse_btn)

        layout.addLayout(dir_row)

        suffix_row = QHBoxLayout()
        self._suffix_label = QLabel()
        self._suffix_label.setStyleSheet("color: #ccc; font-size: 11px; background: transparent;")
        suffix_row.addWidget(self._suffix_label)

        from PyQt6.QtWidgets import QLineEdit
        self._suffix_edit = QLineEdit("_x2")
        self._suffix_edit.setFixedWidth(80)
        suffix_row.addWidget(self._suffix_edit)
        suffix_row.addStretch()

        layout.addLayout(suffix_row)
        self._left_layout.addWidget(frame)

    # ── Language ──────────────────────────────────────────────────

    def _set_language(self, code: str):
        Language.save(code)
        self._apply_language()
        # Update flag button states
        for c, btn in self._flag_buttons.items():
            btn.setChecked(c == code)

    def _on_flag_clicked(self, btn):
        for code, b in self._flag_buttons.items():
            if b is btn:
                self._set_language(code)
                return

    def _apply_language(self):
        """Refresh all visible text from the translation table."""
        self.setWindowTitle(tr("app_title"))
        self._input_title.setText(tr("input_files"))
        self._add_files_btn.setText(tr("add_files"))
        self._add_folder_btn.setText(tr("add_folder"))
        self._clear_btn.setText(tr("clear"))
        self._method_title.setText(tr("method"))
        self._scale_title.setText(tr("scale"))
        self._options_title.setText(tr("options"))
        self._output_title.setText(tr("output"))
        self._browse_btn.setText(tr("browse"))
        self._suffix_label.setText(tr("suffix") + ":")
        self._file_list_label.setText(tr("file_list"))
        self._log_label.setText(tr("log"))
        self._run_btn.setText(tr("run"))
        self._stop_btn.setText(tr("stop"))
        self._open_btn.setText(tr("open_output"))
        self._update_status()
        self._update_file_list()

        # Update bottom bar
        powered = self.findChild(QLabel, "poweredLabel")
        if powered:
            powered.setText(
                f'{tr("powered_by")} '
                f'<a href="https://github.com/ZetHor3" '
                f'style="color: #bb86fc; text-decoration: none;">Mr3ster</a>'
            )
        support = self.findChild(QLabel, "supportLabel")
        if support:
            style = "color: #bb86fc; font-size: 11px; font-weight: bold; background: transparent; text-decoration: underline;"
            support.setStyleSheet(style)
            support.setText(tr("support_us"))

        self._output_dir_label.setText(tr("output_dir_hint"))
        self._update_file_count()

    # ── Engine ────────────────────────────────────────────────────

    def _rebuild_engine(self, method: str = "ncnn"):
        try:
            self._engine = UpscaleEngine(backend_name=method)
            self._update_ai_status()
        except Exception as e:
            self._log(f"[ERROR] {e}")

    def _on_model_changed(self, idx: int):
        """Switch backend+model when user changes model combo."""
        if idx < 0:
            return
        data = self._model_combo.currentData()
        if data.startswith("ncnn:"):
            # ncnn backend
            model_name = data.split(":", 1)[1]
            if not self._engine or self._engine.backend_name != "ncnn":
                self._rebuild_engine("ncnn")
            self._engine.set_options(model=model_name)
            self._log(f"  Режим: ncnn → {model_name}")
        elif data.startswith("py:"):
            # Python realesrgan backend
            model_name = data.split(":", 1)[1]
            try:
                self._rebuild_engine("realesrgan")
                if self._engine.backend.available:
                    self._engine.set_options(model=model_name)
                    self._log(f"  Режим: PyTorch → {model_name} (фотореализм)")
                else:
                    err = getattr(self._engine.backend, '_load_error', 'неизвестная ошибка')
                    self._log(f"  ⚠ Фоторежим недоступен: {err}")
                    self._ai_status_label.setText(f"✗ {err}")
                    self._ai_status_label.setStyleSheet("color: #ff9800; font-size: 10px; background: transparent; padding: 2px 0;")
            except Exception as e:
                self._log(f"  ⚠ Фоторежим недоступен: {e}")
        self._update_options()

    def _update_ai_status(self):
        """Show backend status depending on selected model/backend."""
        if not self._engine:
            self._ai_status_label.setText("")
            return
        bn = self._engine.backend_name
        try:
            if bn == "ncnn":
                if self._engine.backend.available:
                    self._ai_status_label.setText("✓ Vulkan GPU / ncnn (встроенный)")
                    self._ai_status_label.setStyleSheet(
                        "color: #4caf50; font-size: 10px; background: transparent; padding: 2px 0;"
                    )
                else:
                    self._ai_status_label.setText("✗ ncnn бинарник не найден — переустанови проект")
                    self._ai_status_label.setStyleSheet(
                        "color: #ff4444; font-size: 10px; background: transparent; padding: 2px 0;"
                    )
            elif bn == "realesrgan":
                if self._engine.backend.available:
                    self._ai_status_label.setText("✓ CUDA / PyTorch — фотореализм")
                    self._ai_status_label.setStyleSheet(
                        "color: #4caf50; font-size: 10px; background: transparent; padding: 2px 0;"
                    )
                else:
                    err = getattr(self._engine.backend, '_load_error', 'недоступен')
                    self._ai_status_label.setText(f"✗ {err}")
                    self._ai_status_label.setStyleSheet(
                        "color: #ff9800; font-size: 10px; background: transparent; padding: 2px 0;"
                    )
            else:
                self._ai_status_label.setText("")
        except Exception:
            self._ai_status_label.setText("")

    def _update_options(self):
        """Rebuild backend-specific options UI."""
        # Clear existing
        while self._options_container_layout.count():
            item = self._options_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._option_widgets.clear()

        if not self._engine:
            return

        opts = self._engine.get_backend_options()
        if not opts:
            self._options_frame.hide()
            self._options_frame.setVisible(True)
            self._options_frame.hide()
            return

        self._options_frame.show()
        row = 0
        for key, cfg in opts.items():
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)

            label = QLabel(cfg.get("label", key))
            label.setStyleSheet("color: #ccc; font-size: 11px; background: transparent;")
            row_layout.addWidget(label)

            if cfg["type"] == "choice":
                combo = QComboBox()
                choices = cfg.get("choices", [])
                labels = cfg.get("labels", {})
                for c in choices:
                    display = f"{labels[c]} ({c})" if c in labels else c
                    combo.addItem(display, c)
                if cfg.get("value") in choices:
                    idx = choices.index(cfg["value"])
                    combo.setCurrentIndex(idx)
                combo.currentIndexChanged.connect(
                    lambda i, k=key, cb=combo: self._on_option(k, cb.currentData())
                )
                row_layout.addWidget(combo)
                self._option_widgets[key] = combo
            elif cfg["type"] == "float":
                slider = QSlider(Qt.Orientation.Horizontal)
                min_v = cfg.get("min", -1.0)
                max_v = cfg.get("max", 2.0)
                step = cfg.get("step", 0.05)
                current = cfg.get("value", 0.0)
                slider.setRange(int(min_v / step), int(max_v / step))
                slider.setValue(int(current / step))
                val_label = QLabel(f"{current:.2f}")
                val_label.setFixedWidth(36)
                val_label.setStyleSheet("color: #bb86fc; font-size: 11px; background: transparent;")
                slider.valueChanged.connect(
                    lambda v, k=key, vl=val_label, st=step: (
                        vl.setText(f"{v * st:.2f}"),
                        self._on_option(k, v * st)
                    )
                )
                row_layout.addWidget(slider, stretch=1)
                row_layout.addWidget(val_label)
                self._option_widgets[key] = slider
            elif cfg["type"] == "int":
                slider = QSlider(Qt.Orientation.Horizontal)
                min_v = cfg.get("min", 0)
                max_v = cfg.get("max", 1024)
                step = cfg.get("step", 1)
                current = cfg.get("value", min_v)
                slider.setRange(min_v // step, max_v // step)
                slider.setValue(current // step)
                val_label = QLabel(str(current))
                val_label.setFixedWidth(36)
                val_label.setStyleSheet("color: #bb86fc; font-size: 11px; background: transparent;")
                slider.valueChanged.connect(
                    lambda v, k=key, vl=val_label, st=step: (
                        vl.setText(str(v * st)),
                        self._on_option(k, v * st)
                    )
                )
                row_layout.addWidget(slider, stretch=1)
                row_layout.addWidget(val_label)
                self._option_widgets[key] = slider
            elif cfg["type"] == "bool":
                from PyQt6.QtWidgets import QCheckBox
                cb = QCheckBox()
                cb.setChecked(bool(cfg.get("value", False)))
                cb.toggled.connect(lambda v, k=key: self._on_option(k, v))
                row_layout.addWidget(cb)
                self._option_widgets[key] = cb

            self._options_container_layout.addLayout(row_layout)
            row += 1

    def _on_option(self, key: str, value):
        if not self._engine:
            return
        try:
            self._engine.set_options(**{key: value})
        except Exception as e:
            self._log(f"[OPTION ERROR] {key}: {e}")

    # ── Scale ─────────────────────────────────────────────────────

    def _on_scale_changed(self, val: int):
        scale = val / 10.0
        self._scale_value_label.setText(f"{scale:.1f}×")

    def _set_scale(self, val: float):
        self._scale_slider.setValue(int(val * 10))

    # ── File management ───────────────────────────────────────────

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, tr("select_images"),
            "",
            f"{tr('filter_images')};;{tr('all_files')}",
        )
        if files:
            for f in files:
                p = Path(f).resolve()
                if p not in self._file_list:
                    self._file_list.append(p)
            self._update_file_list()

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr("select_folder"))
        if folder:
            imgs = utils.list_images([Path(folder)])
            for p in imgs:
                if p not in self._file_list:
                    self._file_list.append(p)
            self._update_file_list()

    def _clear_files(self):
        self._file_list.clear()
        self._current_results.clear()
        self._update_file_list()
        self._progress_bar.setValue(0)
        self._update_status()

    def _update_file_list(self):
        self._file_widget.clear()
        if not self._file_list:
            self._file_widget.addItem(tr("drag_hint"))
        else:
            for p in self._file_list:
                self._file_widget.addItem(p.name)
        self._update_file_count()

    def _update_file_count(self):
        n = len(self._file_list)
        if n == 0:
            self._file_count_label.setText(tr("no_files"))
        else:
            self._file_count_label.setText(f"{n} {tr('files_selected')}")

    # ── Output ────────────────────────────────────────────────────

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, tr("select_output"))
        if folder:
            self._output_dir_label.setText(folder)
            self._output_dir_label.setStyleSheet("color: #ccc; font-size: 11px; background: transparent;")

    def _open_output(self):
        text = self._output_dir_label.text()
        if text and text != tr("output_dir_hint") and os.path.isdir(text):
            os.startfile(text)
        elif self._file_list:
            folder = self._file_list[0].parent
            if folder and folder.exists():
                os.startfile(str(folder))

    # ── Logging ───────────────────────────────────────────────────

    def _log(self, msg: str):
        self._log_widget.append(msg)
        cursor = self._log_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._log_widget.setTextCursor(cursor)

    # ── Status ────────────────────────────────────────────────────

    def _update_status(self, text: str | None = None):
        if text:
            self._status_label.setText(text)
        else:
            self._status_label.setText(tr("status_ready"))

    # ── Upscale ───────────────────────────────────────────────────

    def _run_upscale(self):
        if not self._file_list:
            QMessageBox.warning(self, tr("no_files_warn"), tr("no_files_msg"))
            return
        if self._thread and self._thread.isRunning():
            return

        # Reset output frame highlight
        self._output_frame.setStyleSheet("QFrame#sectionFrame { border: 1px solid #333; border-radius: 6px; }")

        self._current_results = []
        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._progress_bar.setValue(0)
        self._update_status(tr("status_processing"))
        self._log(f">> {tr('starting')}")

        try:
            # Determine output settings
            out_dir_text = self._output_dir_label.text()
            out_dir = out_dir_text if out_dir_text and out_dir_text != tr("output_dir_hint") else ""

            # Валидация: папка вывода обязательна
            if not out_dir:
                self._output_frame.setStyleSheet(
                    "QFrame#sectionFrame { border: 2px solid #ff4444; border-radius: 6px; }"
                )
                self._run_btn.setEnabled(True)
                self._stop_btn.setEnabled(False)
                self._progress_bar.setValue(0)
                self._update_status(tr("error"))
                self._log("[ERROR] " + tr("no_output_msg"))
                QMessageBox.warning(self, tr("error"), tr("no_output_msg"))
                return
            suffix = self._suffix_edit.text().strip() or "_x2"
            scale = self._scale_slider.value() / 10.0

            # Build engine
            if not self._engine:
                self._engine = UpscaleEngine(backend_name="ncnn")

            # Set any slider options
            for key, widget in self._option_widgets.items():
                if isinstance(widget, QSlider):
                    step = 0.05
                    opt = self._engine.get_backend_options()
                    if key in opt and opt[key].get("type") == "float":
                        step = opt[key].get("step", 0.05)
                    self._engine.set_options(**{key: widget.value() * step})
                elif isinstance(widget, QComboBox):
                    self._engine.set_options(**{key: widget.currentText()})

            self._engine.set_progress_callback(self._on_progress_callback)

            # Build jobs
            jobs = []
            for img_path in self._file_list:
                if not utils.is_image(img_path):
                    continue
                if out_dir:
                    out = Path(out_dir) / f"{img_path.stem}{suffix}{img_path.suffix}"
                else:
                    out = utils.ensure_output_path(img_path, suffix=suffix)
                jobs.append(UpscaleJob(img_path, out, scale=scale))

            self._log(f"  Files: {len(jobs)}  |  Method: Real-ESRGAN ncnn  |  Scale: {scale}×")
            self._log(f"  Device: {self._engine.device}")

            # Setup background thread
            self._worker = UpscaleWorker(self._engine, jobs)
            self._thread = QThread(self)
            self._worker.moveToThread(self._thread)
            self._worker.signals.progress.connect(self._on_progress)
            self._worker.signals.finished.connect(self._on_finished)
            self._thread.started.connect(self._worker.run)
            self._thread.finished.connect(self._thread.deleteLater)
            self._thread.start()

        except Exception as e:
            self._log(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            self._output_frame.setStyleSheet(
                "QFrame#sectionFrame { border: 1px solid #ff4444; border-radius: 6px; }"
            )
            self._run_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._update_status(tr("error"))

    def _stop_upscale(self):
        if self._worker:
            self._worker.stop()
        self._stop_btn.setEnabled(False)
        self._log(f">> {tr('stopping')}")

    def _on_progress_callback(self, completed: int, total: int, job: UpscaleJob):
        """Called from worker thread — use signal instead."""
        pass

    def _on_progress(self, completed: int, total: int, job: UpscaleJob):
        self._progress_bar.setValue(int(completed / max(total, 1) * 100))
        self._progress_bar.setFormat(f"{completed}/{total}")

        if job.error:
            self._log(f"[FAIL] {job.input_path.name}: {job.error}")
        else:
            old_sz = f"{job.input_size[0]}x{job.input_size[1]}" if job.input_size else "?"
            new_sz = f"{job.output_size[0]}x{job.output_size[1]}" if job.output_size else "?"
            self._log(f"[OK]   {job.input_path.name}  {old_sz} -> {new_sz}  {job.duration:.1f}s")

    def _on_finished(self, results: list[UpscaleJob]):
        self._current_results = results
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

        if self._thread:
            self._thread.quit()
            self._thread.wait(2000)
            self._thread = None

        self._progress_bar.setValue(100)
        ok = sum(1 for j in results if not j.error)
        failed = sum(1 for j in results if j.error)

        self._update_status(f"{tr('status_done')}: {ok} {tr('done_ok')}, {failed} {tr('done_failed')}")
        self._log(f">> {tr('status_done')}: {ok} {tr('done_ok')}, {failed} {tr('done_failed')}")

    # ── Cleanup ───────────────────────────────────────────────────

    def closeEvent(self, event):
        if self._worker:
            self._worker.stop()
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)
        super().closeEvent(event)


def run_gui():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#121212"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#252525"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2d2d2d"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#2d2d2d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor("#bb86fc"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#7c4dff"))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)

    window = UpscaleGUI()
    window.show()
    app.exec()
