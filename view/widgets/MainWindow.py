from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QSplitter, QMessageBox, QDockWidget
from PyQt5.QtCore import Qt

from model import ChapterFileWrapper
from view import FileState, FileStateContainer
from view.widgets import ChapterTreeWidget, SegmentTextEdit, OptionsTreeWidget, OperationTreeWidget, ConditionTreeWidget, VariableTreeWidget


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

        self.variable_tree_widget = VariableTreeWidget(self.file_state, self.file.data.variables)
        self.operation_tree_widget = OperationTreeWidget(self.file_state, self.file.data.variables, self.options_tree)
        self.condition_tree_widget = ConditionTreeWidget(self.file_state, self.file.data.variables, self.options_tree)

        # Docks and central widget

        self._set_dock_corners()
        self._create_left_dock_widget()
        self._create_right_dock_widget()
        self._create_bottom_dock_widget()

        self.setCentralWidget(self.segment_text_edit)

        # Signals

        self.save_button.pressed.connect(self._save_file)
        self.segment_text_edit.textChanged.connect(self.chapter_tree.update_selected_segment)

        self.file_state.state_changed.connect(self.on_file_state_changed)

        # Misc
        self.setFont(QFont('Open Sans', 10))
        self.setContentsMargins(5, 5, 5, 5)
        self.resize(1400, 800)
        self.on_file_state_changed(self.file_state.value)

    def _set_dock_corners(self) -> None:
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

    def _create_left_dock_widget(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.chapter_tree)
        layout.addWidget(self.save_button)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        dock = self._create_dock_widget('Древо истории', widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _create_right_dock_widget(self) -> None:
        dock = self._create_dock_widget('Переменные истории', self.variable_tree_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _create_bottom_dock_widget(self) -> None:
        dock = self._create_dock_widget('Опции', self._generate_middle_side())
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def _generate_middle_side(self) -> QWidget:
        splitter = QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(self.options_tree)
        splitter.setCollapsible(0, False)
        splitter.addWidget(self._generate_middle_bottom_side())
        splitter.setCollapsible(1, False)
        splitter.setSizes([200, 200])
        return splitter

    def _generate_middle_bottom_side(self) -> QWidget:
        splitter = QSplitter()
        splitter.addWidget(self.operation_tree_widget)
        splitter.setCollapsible(0, False)
        splitter.addWidget(self.condition_tree_widget)
        splitter.setCollapsible(1, False)
        splitter.setSizes([450, 450])
        return splitter

    def _create_dock_widget(self, title: str, widget: QWidget) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setFloating(False)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        return dock

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
        if self.file_state.value == FileState.DIRTY:
            title = 'Выход'
            msg = 'Остались несохраненные изменения, вы действительно хотите выйти?'
            reply = QMessageBox.question(self, title, msg, QMessageBox.Yes, QMessageBox.No)
            if reply != QMessageBox.Yes:
                event.ignore()
                return

        self.file.close()
        event.accept()
