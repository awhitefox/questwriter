from PyQt5.QtWidgets import QTextEdit, QTreeWidgetItem

from questlib import Chapter
from view import FileStateContainer
from view.widgets import ChapterTreeWidget, widget_utils


class SegmentTextEdit(QTextEdit):
    NO_TARGET_MESSAGE = 'Выберите сегмент истории для редактирования...'

    def __init__(self, file_state: FileStateContainer, chapter: Chapter, tree: ChapterTreeWidget):
        super().__init__()
        self.file_state = file_state
        self.chapter = chapter
        self.segment = None
        self.remove_target()

        self.setAcceptRichText(False)

        self.textChanged.connect(self.on_text_changed)
        tree.currentItemChanged.connect(self.on_tree_current_item_changed)

    def remove_target(self) -> None:
        self.setDisabled(True)
        self.segment = None
        self.setText(self.NO_TARGET_MESSAGE)

    def on_text_changed(self) -> None:
        if self.segment is not None and self.segment.text != self.toPlainText():
            self.segment.text = self.toPlainText()
            self.file_state.set_dirty()

    def on_tree_current_item_changed(self, current: QTreeWidgetItem, _) -> None:
        indexes = widget_utils.tree_widget_item_indexes(current)
        if len(indexes) == 2:  # segment
            self.segment = self.chapter.branches[indexes[0]].segments[indexes[1]]
            self.setText(self.segment.text)
            self.setDisabled(False)
        else:
            self.remove_target()
