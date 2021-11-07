from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QSplitter

from model import ChapterFileWrapper
from view.widgets import ChapterTreeWidget, SegmentTextEdit, OptionsTreeWidget


class MainWindow(QMainWindow):
    def __init__(self, file_path: str):
        super().__init__()
        self.chapter = ChapterFileWrapper(file_path)

        # Widgets

        self.chapter_tree = ChapterTreeWidget(self.chapter)
        self.save_button = QPushButton('Сохранить')
        self.segment_text_edit = SegmentTextEdit(self.chapter, self.chapter_tree)
        self.options_tree = OptionsTreeWidget(self.chapter, self.chapter_tree)

        self.setCentralWidget(self._generate_main_widget())

        # Signals

        self.save_button.pressed.connect(self.chapter.save_changes)
        self.segment_text_edit.textChanged.connect(self.chapter_tree.update_selected_segment)

        refresh_title = [
            self.save_button.pressed,
            self.chapter_tree.itemChanged,
            self.chapter_tree.chapterTreeChanged,
            self.segment_text_edit.textChanged,
            self.options_tree.itemChanged,
            self.options_tree.optionListChanged
        ]
        for e in refresh_title:
            e.connect(self.refresh_title)

        # Misc
        self.setFont(QFont('Open Sans', 10))
        self.resize(1200, 800)
        self.refresh_title()

    def _generate_main_widget(self) -> QWidget:
        splitter = QSplitter()
        splitter.addWidget(self._generate_left_side())
        splitter.addWidget(self._generate_right_side())
        splitter.setSizes([300, 900])
        return splitter

    def _generate_left_side(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.chapter_tree)
        layout.addWidget(self.save_button)
        layout.setContentsMargins(10, 10, 0, 10)
        widget.setLayout(layout)
        return widget

    def _generate_right_side(self) -> QWidget:
        splitter = QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.setContentsMargins(0, 10, 10, 10)
        splitter.addWidget(self.segment_text_edit)
        splitter.addWidget(self.options_tree)
        splitter.setSizes([600, 200])
        return splitter

    def refresh_title(self) -> None:
        s = f'{self.chapter.path} - questwriter'
        if self.chapter.is_dirty():
            s += '*'
        self.setWindowTitle(s)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_S:
            self.chapter.save_changes()
            self.refresh_title()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.chapter.close()
        event.accept()
