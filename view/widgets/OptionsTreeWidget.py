from textwrap import shorten
from typing import Optional

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QComboBox, QMenu, QMessageBox

from questlib import Chapter, Option

from model import default_option
from utils import find_index
from view import FileState, EditorState
from view.widgets import ChapterTreeWidget, widget_utils


class OptionsTreeWidget(QTreeWidget):
    def __init__(self, chapter: Chapter, tree: ChapterTreeWidget):
        super().__init__()
        self.chapter = chapter
        self.options = None
        self.branch_i = None
        self.segment_i = None

        self.setRootIsDecorated(False)
        self.setColumnCount(3)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

        self.itemChanged.connect(self.on_item_changed)
        self.currentItemChanged.connect(self.on_current_item_changed)
        tree.currentItemChanged.connect(self.on_tree_current_item_changed)

        self.setEnabled(False)

    def get_current_option(self) -> Optional[Option]:
        if self.options:
            return self.options[self.indexOfTopLevelItem(self.currentItem())]
        return None

    def _generate_items(self) -> None:
        self.clear()
        if self.options is not None:
            self.setEnabled(True)
            for o in self.options:
                item = self._generate_item(o)
                self.addTopLevelItem(item)
                item.init_widgets(self)
        else:
            self.setEnabled(False)
        EditorState.current_option = None

    def _generate_item(self, option: Option) -> 'OptionsTreeWidgetItem':
        return OptionsTreeWidgetItem(self.chapter, option, self.branch_i, self.segment_i)

    def _context_menu(self, position: QPoint) -> None:
        menu = QMenu()
        menu.addAction('Добавить опцию', self._add_option)

        menu.addSeparator()

        index = self.indexOfTopLevelItem(self.currentItem())
        menu.addAction('Вверх', lambda: self._move_option(-1))
        if index == 0 or len(self.options) == 0:
            menu.actions()[-1].setEnabled(False)
        menu.addAction('Вниз', lambda: self._move_option(1))
        if index + 1 >= len(self.options):
            menu.actions()[-1].setEnabled(False)

        menu.addSeparator()

        menu.addAction('Удалить', self._delete_option)
        if len(self.options) == 1:
            menu.actions()[-1].setEnabled(False)

        menu.exec_(self.viewport().mapToGlobal(position))

    def _add_option(self) -> None:
        selected_i = self.indexOfTopLevelItem(self.currentItem())

        branch = self.chapter.branches[0]
        new = default_option(branch.id, branch.segments[0].id)

        self.options.insert(selected_i + 1, new)
        FileState.set_dirty()

        new_item = self._generate_item(new)
        self.insertTopLevelItem(selected_i + 1, new_item)
        new_item.init_widgets(self)

    def _move_option(self, delta: int) -> None:
        index = self.indexOfTopLevelItem(self.currentItem())

        option = self.options.pop(index)
        self.options.insert(index + delta, option)

        self.takeTopLevelItem(index)
        option_item = self._generate_item(option)
        self.insertTopLevelItem(index + delta, option_item)
        option_item.init_widgets(self)

        self.setCurrentItem(option_item)
        FileState.set_dirty()

    def _delete_option(self) -> None:
        title = 'Удалить'

        selected_i = self.indexOfTopLevelItem(self.currentItem())
        option = self.options[selected_i]

        msg = 'Удалить опцию {0}?'.format(option.text)
        res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            del self.options[selected_i]
            FileState.set_dirty()
            self.takeTopLevelItem(selected_i)

    def on_item_changed(self, item: QTreeWidgetItem, _) -> None:
        option = self.options[self.indexOfTopLevelItem(item)]
        option.text = item.text(0)
        option.goto.branch_id = item.text(1)
        option.goto.segment_id = item.text(2)
        FileState.set_dirty()

    def on_current_item_changed(self, *_) -> None:
        EditorState.current_option = self.get_current_option()

    def on_tree_current_item_changed(self, current: QTreeWidgetItem, _) -> None:
        self.options = None
        self.branch_i = None
        self.segment_i = None
        indexes = widget_utils.tree_widget_item_indexes(current)
        if len(indexes) == 2:  # segment
            br = self.chapter.branches[indexes[0]]
            if not br.is_endings_branch:
                self.options = br.segments[indexes[1]].options
                self.branch_i = indexes[0]
                self.segment_i = indexes[1]
        self._generate_items()


class OptionsTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, chapter: Chapter, o: Option, branch_i: int, segment_i: int):
        super().__init__([o.text, o.goto.branch_id, o.goto.segment_id])
        self.chapter = chapter
        self.option = o
        self.branch_i = branch_i
        self.segment_i = segment_i

        self.setFlags(int(self.flags()) | QtCore.Qt.ItemIsEditable)

        self.branch_combo_box = QComboBox()
        self.branch_combo_box.view().setTextElideMode(QtCore.Qt.ElideRight)
        self.refresh_branch_options()

        self.segment_combo_box = QComboBox()
        self.segment_combo_box.view().setTextElideMode(QtCore.Qt.ElideRight)
        self.refresh_segment_options()

        self.branch_combo_box.currentIndexChanged.connect(self.on_branch_combo_box_index_changed)
        self.segment_combo_box.currentIndexChanged.connect(self.on_segment_combo_box_index_changed)

    def init_widgets(self, tree_widget: QTreeWidget) -> None:
        tree_widget.setItemWidget(self, 1, self.branch_combo_box)
        tree_widget.setItemWidget(self, 2, self.segment_combo_box)

    def refresh_branch_options(self) -> None:
        self.branch_combo_box.clear()
        branch_titles = [b.title if b.title else b.id for b in self.chapter.branches]
        branch_index = find_index(self.chapter.branches, lambda x: x.id == self.option.goto.branch_id)
        self.branch_combo_box.addItems(branch_titles)
        self.branch_combo_box.setCurrentIndex(branch_index)

    def refresh_segment_options(self) -> None:
        self.segment_combo_box.clear()
        branch_index = self.branch_combo_box.currentIndex()
        segments = self.chapter.branches[branch_index].segments
        segment_texts = [shorten(s.text, width=80, placeholder='...').replace('\n', ' ') for s in segments]
        if branch_index == self.branch_i:
            segment_texts[self.segment_i] = '(этот сегмент)'

        segment_index = find_index(self.chapter.branches[branch_index].segments, lambda x: x.id == self.option.goto.segment_id)
        self.segment_combo_box.addItems(segment_texts)
        self.segment_combo_box.setCurrentIndex(segment_index)

    def on_branch_combo_box_index_changed(self, index: int) -> None:
        self.setText(1, self.chapter.branches[index].id)
        self.setText(2, self.chapter.branches[index].segments[0].id)
        self.refresh_segment_options()

    def on_segment_combo_box_index_changed(self, index: int) -> None:
        br_i = self.branch_combo_box.currentIndex()
        self.setText(2, self.chapter.branches[br_i].segments[index].id)
