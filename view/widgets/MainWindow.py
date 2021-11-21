from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QSplitter

from model import ChapterFileWrapper
from view import FileState, FileStateContainer
from view.widgets import ChapterTreeWidget, SegmentTextEdit, OptionsTreeWidget, VariableTreeWidget


class MainWindow(QMainWindow):
    def __init__(self, file_path: str):
        super().__init__()
        self.file = ChapterFileWrapper(file_path)
        self.file_state = FileStateContainer()

        # Widgets

        self.chapter_tree = ChapterTreeWidget(self.file_state, self.file.data)
        self.save_button = QPushButton('Сохранить')
        self.segment_text_edit = SegmentTextEdit(self.file_state, self.chapter_tree)
        self.options_tree = OptionsTreeWidget(self.file_state, self.file.data, self.chapter_tree)

        self.setCentralWidget(self._generate_main_widget())

        # Signals

        self.save_button.pressed.connect(self._save_file)
        self.segment_text_edit.textChanged.connect(self.chapter_tree.update_selected_segment)

        self.file_state.state_changed.connect(self.on_file_state_changed)

        # Misc
        self.setFont(QFont('Open Sans', 10))
        self.resize(1200, 800)
        self.on_file_state_changed(self.file_state.value)

    def _generate_main_widget(self) -> QWidget:
        splitter = QSplitter()
        splitter.addWidget(self._generate_left_side())
        splitter.setCollapsible(0, False)
        splitter.addWidget(self._generate_right_side())
        splitter.setCollapsible(1, False)
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
        splitter.setCollapsible(0, False)
        splitter.addWidget(self.options_tree)
        splitter.setCollapsible(1, False)
        splitter.addWidget(self._generate_right_bottom_side())
        splitter.setCollapsible(2, False)
        splitter.setSizes([400, 200, 200])
        return splitter

    def _generate_right_bottom_side(self) -> QWidget:
        splitter = QSplitter()
        splitter.addWidget(VariableTreeWidget(self.file_state, self.file.data.variables, self.options_tree))
        splitter.setCollapsible(0, False)
        splitter.addWidget(QWidget())
        splitter.setCollapsible(1, False)
        splitter.setSizes([450, 450])
        return splitter

    def _save_file(self):
        self.file.save_changes()
        self.file_state.set_clean()

    def on_file_state_changed(self, state: FileState):
        s = f'{self.file.path} - questwriter'
        if state == FileState.DIRTY:
            s += '*'
        self.setWindowTitle(s)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_S:
            self._save_file()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.file.close()
        event.accept()
