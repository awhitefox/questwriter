from typing import Union

from PyQt5.QtWidgets import QTextEdit, QPlainTextEdit

from questlib import Chapter, Branch, Segment
from view import FileStateContainer
from view.widgets import ChapterTreeWidget


class SegmentTextEdit(QPlainTextEdit):
    NO_TARGET_MESSAGE = 'Выберите сегмент истории для редактирования...'

    def __init__(self, file_state: FileStateContainer, tree: ChapterTreeWidget):
        super().__init__()
        self.file_state = file_state
        self.segment = None
        self._disable()

        self.textChanged.connect(self.on_text_changed)
        tree.current_story_element_changed.connect(self.on_tree_current_story_element_changed)

    def _disable(self) -> None:
        self.setEnabled(False)
        self.setPlainText(self.NO_TARGET_MESSAGE)

    def on_text_changed(self) -> None:
        if self.segment is not None and self.segment.text != self.toPlainText():
            self.segment.text = self.toPlainText()
            self.file_state.set_dirty()

    def on_tree_current_story_element_changed(self, element: Union[Chapter, Branch, Segment]):
        if isinstance(element, Segment):
            self.segment = element
            self.setPlainText(element.text)
            self.setEnabled(True)
        else:
            self.segment = None
            self._disable()
