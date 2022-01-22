from typing import Optional

from PyQt5.QtWidgets import QPlainTextEdit
from questlib import Segment

from view import FileState, EditorState


class SegmentTextEdit(QPlainTextEdit):
    NO_TARGET_MESSAGE = 'Выберите сегмент истории для редактирования...'

    def __init__(self):
        super().__init__()
        self.segment = None
        self._disable()

        self.textChanged.connect(self.on_text_changed)
        EditorState.current_segment_changed.connect(self.on_current_segment_changed)

    def _disable(self) -> None:
        self.setEnabled(False)
        self.setPlainText(self.NO_TARGET_MESSAGE)

    def on_text_changed(self) -> None:
        if self.segment is not None and self.segment.text != self.toPlainText():
            self.segment.text = self.toPlainText()
            FileState.set_dirty()

    def on_current_segment_changed(self, segment: Optional[Segment]):
        if segment is not None:
            self.segment = segment
            self.setPlainText(segment.text)
            self.setEnabled(True)
        else:
            self.segment = None
            self._disable()
