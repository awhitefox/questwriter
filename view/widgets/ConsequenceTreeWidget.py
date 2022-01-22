from typing import List, Optional, Type

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QComboBox, QMenu, QMessageBox, QDoubleSpinBox
from questlib import Option, Variable, Consequence, Operation

from model.defaults import default_consequence
from utils import find_index
from view import FileState, EditorState
from view.widgets import BoolComboBox


class ConsequenceTreeWidget(QTreeWidget):
    def __init__(self, variables: List[Variable]):
        super().__init__()
        self.variables = variables
        self.option: Optional[Option] = None

        self.setColumnCount(3)
        self.header().setStretchLastSection(False)
        self.header().setMinimumSectionSize(80)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

        EditorState.current_option_changed.connect(self.on_current_option_changed)
        self.setEnabled(False)

    def _generate_items(self) -> None:
        self.clear()
        if self.option.consequences is not None:
            self.setEnabled(True)
            for o in self.option.consequences:
                item = self._generate_item(o)
                self.addTopLevelItem(item)
                item.init_widgets(self)
        else:
            self.setEnabled(False)

    def _generate_item(self, consequence: Consequence) -> 'ConsequenceTreeWidgetItem':
        return ConsequenceTreeWidgetItem(self.variables, consequence)

    def _context_menu(self, position: QPoint) -> None:
        menu = QMenu()

        menu.addAction('Добавить последствие', self._add_consequence)
        menu.actions()[-1].setEnabled(len(self.variables) > 0)

        menu.addSeparator()

        index = self.indexOfTopLevelItem(self.currentItem())
        menu.addAction('Вверх', lambda: self._move_consequence(-1))
        if index == 0 or len(self.option.consequences) == 0:
            menu.actions()[-1].setEnabled(False)
        menu.addAction('Вниз', lambda: self._move_consequence(1))
        if index + 1 >= len(self.option.consequences):
            menu.actions()[-1].setEnabled(False)

        menu.addSeparator()

        menu.addAction('Удалить', self._delete_consequence)
        menu.actions()[-1].setEnabled(bool(self.option.consequences))

        menu.exec_(self.viewport().mapToGlobal(position))

    def _add_consequence(self) -> None:
        selected_i = self.indexOfTopLevelItem(self.currentItem())
        new = default_consequence(self.variables[0])
        self.option.consequences.insert(selected_i + 1, new)
        FileState.set_dirty()

        new_item = self._generate_item(new)
        self.insertTopLevelItem(selected_i + 1, new_item)
        new_item.init_widgets(self)

    def _move_consequence(self, delta: int) -> None:
        index = self.indexOfTopLevelItem(self.currentItem())

        consequence = self.option.consequences.pop(index)
        self.option.consequences.insert(index + delta, consequence)

        self.takeTopLevelItem(index)
        consequence_item = self._generate_item(consequence)
        self.insertTopLevelItem(index + delta, consequence_item)
        consequence_item.init_widgets(self)

        self.setCurrentItem(consequence_item)
        FileState.set_dirty()

    def _delete_consequence(self) -> None:
        title = 'Удалить'

        selected_i = self.indexOfTopLevelItem(self.currentItem())

        msg = 'Удалить последствие?'
        res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            del self.option.consequences[selected_i]
            FileState.set_dirty()
            self.takeTopLevelItem(selected_i)

    def on_current_option_changed(self, o: Optional[Option]) -> None:
        if o is not None:
            self.option = o
            self._generate_items()
            self.setEnabled(True)
        else:
            self.option = None
            self.clear()
            self.setEnabled(False)


class ConsequenceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, variables: List[Variable], c: Consequence):
        super().__init__()
        self.variables = variables
        self.consequence = c
        self._tree = None

        current_index = find_index(variables, lambda x: x.id == c.variable_id)
        self.variable_type = self.variables[current_index].type

        self.variable_combo_box = QComboBox()
        self.variable_combo_box.view().setTextElideMode(QtCore.Qt.ElideRight)
        self.type_combo_box = QComboBox()
        self.value_widget = None

        self.variable_combo_box.addItems(map(lambda x: x.name, self.variables))
        self.variable_combo_box.setCurrentIndex(current_index)

        self._set_variable_type(self.variables[current_index].type)

        self.variable_combo_box.currentIndexChanged.connect(self.on_variable_change)
        self.type_combo_box.currentIndexChanged.connect(self.on_type_change)

    def init_widgets(self, tree_widget: QTreeWidget) -> None:
        self._tree = tree_widget
        tree_widget.setItemWidget(self, 0, self.variable_combo_box)
        tree_widget.setItemWidget(self, 1, self.type_combo_box)
        tree_widget.setItemWidget(self, 2, self.value_widget)

    def _set_variable_type(self, var_type: Type) -> None:
        if self.value_widget is not None:
            self.value_widget.disconnect()

        b = self.type_combo_box.blockSignals(True)
        self.type_combo_box.clear()
        self.type_combo_box.addItems((i.value for i in Operation if i.is_available_for(var_type)))
        self.type_combo_box.blockSignals(b)

        if not self.consequence.type.is_available_for(var_type):
            self.consequence.type = Operation.Set
        self.type_combo_box.setCurrentIndex(list(Operation).index(self.consequence.type))

        if var_type is bool:
            if type(self.consequence.value) is not var_type:
                self.consequence.value = False

            self.value_widget = BoolComboBox()
            self.value_widget.value = self.consequence.value
            self.value_widget.value_changed.connect(self.on_value_change)
        elif var_type is float:
            if type(self.consequence.value) is not var_type:
                self.consequence.value = 0.0

            self.value_widget = QDoubleSpinBox()
            self.value_widget.setValue(self.consequence.value)
            self.value_widget.setRange(-float('inf'), float('inf'))
            self.value_widget.valueChanged.connect(self.on_value_change)
        else:
            raise ValueError(f'Variable type {var_type} not supported')

        if self._tree is not None:
            self._tree.setItemWidget(self, 2, self.value_widget)

    def on_variable_change(self, index: int) -> None:
        new = self.variables[index]
        if type(self.consequence.value) is not new.type:
            self._set_variable_type(new.type)
        self.consequence.variable_id = new.id
        FileState.set_dirty()

    def on_type_change(self, *_) -> None:
        self.consequence.type = Operation(self.type_combo_box.currentText())
        FileState.set_dirty()

    def on_value_change(self, *_):
        if isinstance(self.value_widget, BoolComboBox):
            self.consequence.value = self.value_widget.value
        elif isinstance(self.value_widget, QDoubleSpinBox):
            self.consequence.value = self.value_widget.value()
        FileState.set_dirty()
