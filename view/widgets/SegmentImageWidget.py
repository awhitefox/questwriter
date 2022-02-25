from typing import Optional, Dict

import requests
from PyQt5.QtCore import Qt, QThread, QObject
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QFrame, QProgressDialog
from questlib import Segment

from view import FileState, EditorState


class SegmentImageWidget(QFrame):
    S_NO_SEGMENT = 'Сегмент не выбран'
    S_NO_IMAGE = 'Нет иллюстрации'
    S_NOT_LOADED = 'Превью не загружено'
    S_FAILED_TO_LOAD = 'Ошибка при загрузке превью'

    def __init__(self):
        super().__init__()
        self.segment: Optional[Segment] = None
        self.images: Dict[str, Optional[QImage]] = {}
        self.OLD = None
        self.setFrameShape(QFrame.StyledPanel)

        self.url_widget = QLineEdit()
        self.remove_button = QPushButton('Удалить')
        self.change_button = QPushButton('Заменить')
        self.image_widget = QLabel()

        self.url_widget.setPlaceholderText('URL')
        self.image_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_widget.setAlignment(Qt.AlignCenter)
        self.image_widget.setFrameShape(QFrame.StyledPanel)
        self.image_widget.setMinimumSize(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.image_widget)
        layout.addWidget(self.url_widget)
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(self.remove_button)
        sub_layout.addWidget(self.change_button)
        layout.addLayout(sub_layout)

        self.setLayout(layout)

        self._disable()
        EditorState.current_segment_changed.connect(self.on_current_segment_changed)

        self.change_button.pressed.connect(self._change_image)
        self.remove_button.pressed.connect(self._remove_image)

    def _update_label(self) -> None:
        if self.segment is None:
            self.image_widget.setText(self.S_NO_SEGMENT)
            return

        if self.segment.id not in self.images:
            self.image_widget.setText(self.S_NOT_LOADED if self.segment.image_url else self.S_NO_IMAGE)
            return

        image = self.images[self.segment.id]
        if image is not None:
            w = self.image_widget.width() - self.image_widget.lineWidth() * 2
            h = self.image_widget.height() - self.image_widget.lineWidth() * 2
            self.image_widget.setPixmap(QPixmap(image).scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_widget.setText(self.S_FAILED_TO_LOAD)

    def _change_image(self, *, manual: bool = True) -> None:
        if manual and self.segment.image_url:
            title = 'Заменить'
            msg = 'Вы точно хотите заменить иллюстрацию? Это действие нельзя будет отменить.'
            res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if res != QMessageBox.Yes:
                return

        url = self.url_widget.text()
        if not url:
            self._remove_image()

        dialog = QProgressDialog('Скачиваем превью...', 'Отмена', 0, 0, self)
        dialog.setWindowTitle('Иллюстрация')
        dialog.setWindowModality(Qt.WindowModal)

        thread = ImageDownloadThread(self, url, self.segment.id)
        thread.finished.connect(dialog.hide)
        dialog.canceled.connect(thread.terminate)
        thread.start()
        dialog.exec()

        cancelled = dialog.wasCanceled()
        dialog.close()
        if cancelled:
            return

        self.images[self.segment.id] = None if thread.has_failed else thread.result
        self.remove_button.setEnabled(True)
        self._update_label()
        if manual:
            self.segment.image_url = url
            FileState.set_dirty()

    def _remove_image(self):
        title = 'Удалить'
        msg = 'Вы точно хотите удалить иллюстрацию? Это действие нельзя будет отменить.'
        res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res != QMessageBox.Yes:
            return

        self.segment.image_url = None
        del self.images[self.segment.id]
        self._update_label()
        self.url_widget.setText('')
        self.remove_button.setEnabled(False)
        FileState.set_dirty()

    def _enable(self) -> None:
        self.url_widget.setText(self.segment.image_url)

        if self.segment.image_url is None:
            self.image_widget.setText(self.S_NO_IMAGE)
        else:
            self.image_widget.setText(self.S_NOT_LOADED)
            self.url_widget.setText(self.segment.image_url)
            if self.segment.id in self.images:
                self._update_label()
            else:
                self._change_image(manual=False)

        self.url_widget.setEnabled(True)
        self.remove_button.setEnabled(self.segment.id in self.images)
        self.change_button.setEnabled(True)

    def _disable(self) -> None:
        self.url_widget.setText('')
        self.segment = None
        self._update_label()

        self.url_widget.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.change_button.setEnabled(False)

    def on_current_segment_changed(self, segment: Optional[Segment]):
        if segment is not None:
            self.segment = segment
            self._enable()
        else:
            self._disable()

    def resizeEvent(self, _) -> None:
        self._update_label()


class ImageDownloadThread(QThread):
    def __init__(self, parent: QObject, url: str, segment_id: str):
        super().__init__(parent)
        self.url: str = url
        self.segment_id: str = segment_id

        self.result: Optional[QImage] = None
        self.has_failed = False
        self.exception: Optional[Exception] = None

    def run(self) -> None:
        try:
            image = QImage()
            self.has_failed = not image.loadFromData(requests.get(self.url).content)
            self.result = image
        except Exception as e:
            self.has_failed = True
            self.exception = e
