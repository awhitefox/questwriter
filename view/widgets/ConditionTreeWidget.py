from typing import List, Optional, Type

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QComboBox, QMenu, QMessageBox, QCheckBox, QDoubleSpinBox, QInputDialog
from questlib import Option, VariableDefinition, Condition, ComparisonType, CompareTo

from model.defaults import default_condition
from utils import find_index, find
from view import FileState, EditorState


class ConditionTreeWidget(QTreeWidget):
    def __init__(self, variables: List[VariableDefinition]):
        super().__init__()
        self.variables = variables
        self.option = None

        self.setColumnCount(3)
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

        EditorState.current_option_changed.connect(self.on_current_option_changed)
        self.setEnabled(False)

    def _generate_items(self) -> None:
        self.clear()
        if self.option.conditions is not None:
            self.setEnabled(True)
            for o in self.option.conditions:
                item = self._generate_item(o)
                self.addTopLevelItem(item)
                item.init_widgets(self)
        else:
            self.setEnabled(False)

    def _generate_item(self, condition: Condition) -> 'ConditionTreeWidgetItem':
        return ConditionTreeWidgetItem(self.variables, condition)

    def _context_menu(self, position: QPoint) -> None:
        menu = QMenu()

        menu.addAction('Добавить условие', self._add_condition)
        menu.actions()[-1].setEnabled(len(self.variables) > 0)

        menu.addSeparator()

        menu.addAction('Удалить', self._delete_condition)
        menu.actions()[-1].setEnabled(bool(self.option.conditions))

        menu.exec_(self.viewport().mapToGlobal(position))

    def _add_condition(self) -> None:
        selected_i = self.indexOfTopLevelItem(self.currentItem())
        new = default_condition(self.variables[0])
        self.option.conditions.insert(selected_i + 1, new)
        FileState.set_dirty()

        new_item = self._generate_item(new)
        self.insertTopLevelItem(selected_i + 1, new_item)
        new_item.init_widgets(self)

    def _delete_condition(self) -> None:
        title = 'Удалить'

        selected_i = self.indexOfTopLevelItem(self.currentItem())

        msg = 'Удалить условие?'
        res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            del self.option.conditions[selected_i]
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


class ConditionTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, variables: List[VariableDefinition], c: Condition):
        super().__init__()
        self.variables = variables
        self.condition = c
        self._tree = None

        current_index = find_index(variables, lambda x: x.id == c.left)
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
        if self.condition.compare_to == CompareTo.Variable:
            raise AttributeError('Comparison to variables is not supported yet')  # TODO

        if self.value_widget is not None:
            self.value_widget.disconnect()

        b = self.type_combo_box.blockSignals(True)
        self.type_combo_box.clear()
        self.type_combo_box.addItems((i.value for i in ComparisonType if i.is_available_for(var_type)))
        self.type_combo_box.blockSignals(b)

        if not self.condition.comparison.is_available_for(var_type):
            self.condition.comparison = ComparisonType.Equal
        self.type_combo_box.setCurrentIndex(list(ComparisonType).index(self.condition.comparison))

        if var_type is bool:
            if type(self.condition.right) is not var_type:
                self.condition.right = False

            self.value_widget = QCheckBox()
            self.value_widget.setCheckState(2 if self.condition.right else 0)  # use 2 to avoid tristate
            self.value_widget.stateChanged.connect(self.on_value_change)
        elif var_type is float:
            if type(self.condition.right) is not var_type:
                self.condition.right = 0.0

            self.value_widget = QDoubleSpinBox()
            self.value_widget.setValue(self.condition.right)
            self.value_widget.setRange(-float('inf'), float('inf'))
            self.value_widget.valueChanged.connect(self.on_value_change)
        else:
            raise ValueError(f'Variable type {var_type} not supported')

        if self._tree is not None:
            self._tree.setItemWidget(self, 2, self.value_widget)

    def on_variable_change(self, index: int) -> None:
        new = self.variables[index]
        if type(self.condition.right) is not new.type:
            self._set_variable_type(new.type)
        self.condition.left = new.id
        FileState.set_dirty()

    def on_type_change(self, *_) -> None:
        self.condition.comparison = ComparisonType(self.type_combo_box.currentText())
        FileState.set_dirty()

    def on_value_change(self, *_):
        if isinstance(self.value_widget, QCheckBox):
            self.condition.right = bool(self.value_widget.checkState())  # convert to bool to avoid tristate
        elif isinstance(self.value_widget, QDoubleSpinBox):
            self.condition.right = self.value_widget.value()
        FileState.set_dirty()
