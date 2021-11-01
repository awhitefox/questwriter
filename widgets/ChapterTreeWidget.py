import textwrap
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox

from model import ChapterFileWrapper, generate_new_branch, generate_new_segment
from widgets import widget_utils


class ChapterTreeWidget(QTreeWidget):
    chapterTreeChanged = pyqtSignal()

    def __init__(self, chapter: ChapterFileWrapper):
        super().__init__()
        self.chapter = chapter

        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self._generate_tree()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

        self.itemChanged.connect(self.on_item_changed)

        self.expandAll()

    def _generate_tree(self) -> None:
        self.clear()
        root = QTreeWidgetItem([self.chapter.data['title']])
        root.setFlags(root.flags() | QtCore.Qt.ItemIsEditable)

        for br in self.chapter.data['branches']:
            root.addChild(self._generate_branch_item(br))

        self.addTopLevelItem(root)

    def _generate_branch_item(self, branch: dict) -> QTreeWidgetItem:
        if branch['id'].startswith('@'):
            br_item = QTreeWidgetItem([branch['id']])
        else:
            br_item = QTreeWidgetItem([branch['title']])
            br_item.setFlags(br_item.flags() | QtCore.Qt.ItemIsEditable)

        for seg in branch['segments']:
            br_item.addChild(self._generate_segment_item(seg))

        return br_item

    # noinspection PyMethodMayBeStatic
    def _generate_segment_item(self, segment: dict) -> QTreeWidgetItem:
        return QTreeWidgetItem([segment['text'].replace('\n', '')])

    def _context_menu(self, position: QPoint) -> None:
        indexes = widget_utils.tree_widget_item_indexes(self.currentItem())

        menu = QMenu()
        menu.addAction('Добавить ветвь', self._add_branch)
        if len(indexes) != 0:
            if self.chapter.data['branches'][indexes[0]]['id'] != '@endings':
                menu.addAction('Добавить сегмент', self._add_segment)
            else:
                menu.addAction('Добавить концовку', self._add_segment)
            menu.addSeparator()
            if len(indexes) == 1:
                menu.addAction('Удалить', self._delete_branch)
                if self.chapter.data['branches'][indexes[0]]['id'][0] == '@':
                    menu.actions()[-1].setEnabled(False)
            else:
                menu.addAction('Удалить', self._delete_segment)
                if len(self.chapter.data['branches'][indexes[0]]['segments']) == 1:
                    menu.actions()[-1].setEnabled(False)

        menu.exec_(self.viewport().mapToGlobal(position))

    def _add_branch(self) -> None:
        indexes = widget_utils.tree_widget_item_indexes(self.currentItem())
        br_count = len(self.chapter.data['branches'])
        if len(indexes) == 0:
            target = br_count - 1  # insert before @endings
        else:
            target = indexes[0] + 1
            if target == br_count:
                target -= 1

        new = generate_new_branch()
        goto = new['segments'][0]['options'][0]['goto']
        goto['branch_id'] = self.chapter.data['branches'][0]['id']
        goto['segment_id'] = self.chapter.data['branches'][0]['segments'][0]['id']
        self.chapter.data['branches'].insert(target, new)
        self.chapter.mark_dirty()

        new_item = self._generate_branch_item(new)
        self.topLevelItem(0).insertChild(target, new_item)
        new_item.setExpanded(True)

        # noinspection PyUnresolvedReferences
        self.chapterTreeChanged.emit()

    def _add_segment(self) -> None:
        indexes = widget_utils.tree_widget_item_indexes(self.currentItem())
        if len(indexes) == 1:
            target = len(self.chapter.data['branches'][indexes[0]]['segments'])
        elif len(indexes) == 2:
            target = indexes[1] + 1
        else:
            return

        new = generate_new_segment()
        if self.chapter.data['branches'][indexes[0]]['id'] != '@endings':
            goto = new['options'][0]['goto']
            goto['branch_id'] = self.chapter.data['branches'][0]['id']
            goto['segment_id'] = self.chapter.data['branches'][0]['segments'][0]['id']
        else:
            new['text'] = 'Новая концовка'
            del new['options']
        self.chapter.data['branches'][indexes[0]]['segments'].insert(target, new)
        self.chapter.mark_dirty()

        new_item = self._generate_segment_item(new)
        self.topLevelItem(0).child(indexes[0]).insertChild(target, new_item)

        # noinspection PyUnresolvedReferences
        self.chapterTreeChanged.emit()

    def _delete_branch(self) -> None:
        title = 'Удалить'

        indexes = widget_utils.tree_widget_item_indexes(self.currentItem())
        branch = self.chapter.data['branches'][indexes[0]]

        msg = 'Удалить ветвь {0}?'.format(branch['title'])
        res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            del self.chapter.data['branches'][indexes[0]]
            self._cleanup_options_after_branch_deletion(branch['id'])
            self.chapter.mark_dirty()

            item = self.topLevelItem(0).child(indexes[0])
            self.topLevelItem(0).removeChild(item)

            # noinspection PyUnresolvedReferences
            self.chapterTreeChanged.emit()

    def _delete_segment(self) -> None:
        title = 'Удалить'

        indexes = widget_utils.tree_widget_item_indexes(self.currentItem())
        segment = self.chapter.data['branches'][indexes[0]]['segments'][indexes[1]]

        msg = 'Удалить сегмент {0}?'.format(textwrap.shorten(segment['text'], width=15, placeholder='...'))
        res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            del self.chapter.data['branches'][indexes[0]]['segments'][indexes[1]]
            self._cleanup_options_after_segment_deletion(segment['id'])
            self.chapter.mark_dirty()

            item = self.topLevelItem(0).child(indexes[0]).child(indexes[1])
            self.topLevelItem(0).child(indexes[0]).removeChild(item)

            # noinspection PyUnresolvedReferences
            self.chapterTreeChanged.emit()

    def _cleanup_options_after_branch_deletion(self, deleted_branch_id: str) -> None:
        br_id = self.chapter.data['branches'][0]['id']
        seg_id = self.chapter.data['branches'][0]['segments'][0]['id']

        for br in self.chapter.data['branches']:
            for seg in br['segments']:
                for opt in seg.get('options', ()):
                    goto = opt['goto']
                    if goto['branch_id'] == deleted_branch_id:
                        goto['branch_id'] = br_id
                        goto['segment_id'] = seg_id

    def _cleanup_options_after_segment_deletion(self, deleted_segment_id: int) -> None:
        br_id = self.chapter.data['branches'][0]['id']
        seg_id = self.chapter.data['branches'][0]['segments'][0]['id']

        for br in self.chapter.data['branches']:
            for seg in br['segments']:
                for opt in seg.get('options', ()):
                    goto = opt['goto']
                    if goto['segment_id'] == deleted_segment_id:
                        goto['branch_id'] = br_id
                        goto['segment_id'] = seg_id

    def update_selected_segment(self) -> None:
        indexes = widget_utils.tree_widget_item_indexes(self.currentItem())
        if len(indexes) != 2:
            return
        text = self.chapter.data['branches'][indexes[0]]['segments'][indexes[1]]['text']
        self.currentItem().setText(0, text.replace('\n', ''))

    def on_item_changed(self, item: QTreeWidgetItem, _) -> None:
        indexes = widget_utils.tree_widget_item_indexes(item)
        if len(indexes) == 0:  # chapter title
            self.chapter.data['title'] = item.text(0)
            self.chapter.mark_dirty()
        elif len(indexes) == 1:  # branch title
            self.chapter.data['branches'][indexes[0]]['title'] = item.text(0)
            self.chapter.mark_dirty()
