from typing import Callable

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, QDockWidget, QApplication, QActionGroup, QAction, QFontDialog

from model import ChapterFileWrapper
from view import FileState
from view.palettes import DarkPalette
from view.widgets import ChapterTreeWidget, SegmentTextEdit, OptionsTreeWidget, ConsequenceTreeWidget, RequirementTreeWidget, VariableTreeWidget


class MainWindow(QMainWindow):
    def __init__(self, file_path: str):
        super().__init__()
        self.file = ChapterFileWrapper(file_path)

        # Widgets

        self.chapter_tree = ChapterTreeWidget(self.file.data)
        self.segment_text_edit = SegmentTextEdit()
        self.options_tree = OptionsTreeWidget(self.file.data, self.chapter_tree)

        self.variable_tree_widget = VariableTreeWidget(self.file.data)
        self.consequence_tree_widget = ConsequenceTreeWidget(self.file.data.variables)
        self.requirement_tree_widget = RequirementTreeWidget(self.file.data.variables)

        # Docks and central widget

        self._set_dock_corners()
        self._create_left_dock_widget()
        self._create_right_dock_widget()
        self._create_bottom_dock_widgets()

        self.setDockNestingEnabled(True)
        self.setCentralWidget(self.segment_text_edit)

        # Menu

        file_menu = self.menuBar().addMenu('Файл')
        file_menu.addAction('Сохранить', self._save_file)
        file_menu.addSeparator()
        file_menu.addAction('Выход', self._exit)

        appearance_menu = self.menuBar().addMenu('Вид')

        font_menu = appearance_menu.addMenu('Шрифт')
        font_menu.addAction('Изменить...', self._change_font)
        font_menu.addAction('По умолчанию', lambda: self.setFont(self.default_font))

        themes_menu = appearance_menu.addMenu('Темы')
        themes_group = QActionGroup(self)
        themes_group.addAction(_create_action('Стандартная', lambda: QApplication.setPalette(self.default_palette))).setCheckable(True)
        themes_group.addAction(_create_action('Тёмная', lambda: QApplication.setPalette(DarkPalette()))).setCheckable(True)
        themes_group.actions()[0].setChecked(True)
        themes_group.setExclusive(True)
        themes_menu.addActions(themes_group.actions())

        window_menu = self.menuBar().addMenu('Окна')
        window_menu.addActions(self.createPopupMenu().actions())

        # Signals

        self.segment_text_edit.textChanged.connect(self.chapter_tree.update_selected_segment)
        FileState.state_changed.connect(self.on_file_state_changed)

        # Misc
        QApplication.setStyle("Fusion")
        self.default_font = QApplication.font()
        self.default_font.setPointSize(10)
        self.setFont(self.default_font)
        self.default_palette = QApplication.palette()

        self.setContentsMargins(5, 5, 5, 5)
        self.resize(1400, 800)
        self.on_file_state_changed(FileState.is_dirty)

    def _set_dock_corners(self) -> None:
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

    def _create_left_dock_widget(self) -> None:
        dock = self._create_dock_widget('Древо истории', self.chapter_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _create_right_dock_widget(self) -> None:
        dock = self._create_dock_widget('Переменные истории', self.variable_tree_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _create_bottom_dock_widgets(self) -> None:
        top_dock = self._create_dock_widget('Опции', self.options_tree)
        left_dock = self._create_dock_widget('Последствия', self.consequence_tree_widget)
        right_dock = self._create_dock_widget('Требования', self.requirement_tree_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, top_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, left_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, right_dock)
        self.splitDockWidget(top_dock, right_dock, Qt.Vertical)
        self.splitDockWidget(right_dock, left_dock, Qt.Horizontal)

    def _create_dock_widget(self, title: str, widget: QWidget) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setFloating(False)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        return dock

    def _save_file(self):
        self.file.save_changes()
        FileState.set_clean()

    def _exit(self):
        self.close()

    def _change_font(self):
        font, ok = QFontDialog.getFont(self.font(), self, 'Изменить шрифт', QFontDialog.FontDialogOptions())
        if ok is True:
            self.setFont(font)

    def on_file_state_changed(self, is_dirty: FileState):
        s = f'{self.file.path} - questwriter'
        if is_dirty:
            s += '*'
        self.setWindowTitle(s)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_S:
            self._save_file()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if FileState.is_dirty:
            message_box = QMessageBox(QMessageBox.Warning,
                                      'Выход',
                                      'Файл имеет несохраненные изменения, выберите действие.')
            save_b = message_box.addButton('Сохранить', QMessageBox.AcceptRole)
            dont_save_b = message_box.addButton('Не сохранять', QMessageBox.DestructiveRole)
            message_box.addButton('Отмена', QMessageBox.RejectRole)
            message_box.setDefaultButton(save_b)
            message_box.exec()

            if message_box.clickedButton() == save_b:
                self.file.save_changes()
            elif message_box.clickedButton() == dont_save_b:
                pass
            else:
                event.ignore()
                return

        self.file.close()
        event.accept()


def _create_action(name: str, func: Callable[[], None]) -> QAction:
    action = QAction(name)
    action.triggered.connect(func)
    return action
