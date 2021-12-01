from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QComboBox, QMenu, QMessageBox, QCheckBox, QDoubleSpinBox

from questlib import Option, VariableDefinition, VariableOperation, OperationType
from utils import find_index
from view import FileStateContainer
from view.widgets import OptionsTreeWidget


class OperationTreeWidget(QTreeWidget):
    def __init__(self, file_state: FileStateContainer, variables: List[VariableDefinition], opt_edit: OptionsTreeWidget):
        super().__init__()
        self.file_state = file_state
        self.variables = variables
        self.operations = None
        self.branch_i = None
        self.segment_i = None

        self.setColumnCount(3)
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

        opt_edit.current_option_changed.connect(self.on_current_option_changed)

        self.setEnabled(False)

    def _generate_items(self) -> None:
        self.clear()
        if self.operations is not None:
            self.setEnabled(True)
            for o in self.operations:
                item = self._generate_item(o)
                self.addTopLevelItem(item)
                item.init_widgets(self)
        else:
            self.setEnabled(False)

    def _generate_item(self, operation: VariableOperation) -> 'OperationTreeWidgetItemBase':
        return OperationTreeWidgetItemBase(self.file_state, self.variables, operation)

    def _context_menu(self, position: QPoint) -> None:
        menu = QMenu()

        menu.addAction('Добавить последствие', self._add_operation)
        menu.actions()[-1].setEnabled(len(self.variables) > 0)

        menu.addSeparator()

        menu.addAction('Удалить', self._delete_operation)
        menu.actions()[-1].setEnabled(len(self.options) > 1)

        menu.exec_(self.viewport().mapToGlobal(position))

    def _add_operation(self) -> None:
        selected_i = self.indexOfTopLevelItem(self.currentItem())

        new = VariableOperation()
        new.variable_id = self.variables[0].id
        new.type = OperationType.Set
        new.value = self.variables[0].initial_value

        self.operations.insert(selected_i + 1, new)
        self.file_state.set_dirty()

        new_item = self._generate_item(new)
        self.insertTopLevelItem(selected_i + 1, new_item)
        new_item.init_widgets(self)

    def _delete_operation(self) -> None:
        title = 'Удалить'

        selected_i = self.indexOfTopLevelItem(self.currentItem())

        msg = 'Удалить последствие?'
        res = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            del self.operation[selected_i]
            self.file_state.set_dirty()
            self.takeTopLevelItem(selected_i)

    def on_current_option_changed(self, o: Option) -> None:
        if o is not None:
            self.operations = o.operations
            self._generate_items()
            self.setEnabled(True)
        else:
            self.operations = None
            self.setEnabled(False)


class OperationTreeWidgetItemBase(QTreeWidgetItem):
    def __init__(self, file_state: FileStateContainer, variables: List[VariableDefinition], o: VariableOperation):
        super().__init__()
        self.file_state = file_state
        self.variables = variables
        self.operation = o

        self.variable_combo_box = QComboBox()
        self.variable_combo_box.view().setTextElideMode(QtCore.Qt.ElideRight)
        self.variable_combo_box.addItems(map(lambda x: x.name, variables))
        self.variable_combo_box.setCurrentIndex(find_index(variables, lambda x: x.id == o.variable_id))

        self.type_combo_box = QComboBox()
        self.type_combo_box.addItems(map(lambda x: x.value, OperationType))
        self.type_combo_box.setCurrentIndex(list(OperationType).index(o.type))

        self.value_widget = None

    def init_widgets(self, tree_widget: QTreeWidget) -> None:
        tree_widget.setItemWidget(self, 0, self.variable_combo_box)
        tree_widget.setItemWidget(self, 1, self.type_combo_box)
        tree_widget.setItemWidget(self, 2, self.value_widget)

    def on_variable_combo_box_index_changed(self, index: int) -> None:
        self.operation.variable_id = self.variables[index].id
        self.file_state.set_dirty()

    def on_type_combo_box_index_changed(self, _: int) -> None:
        self.operation.type = OperationType(self.type_combo_box.currentText())
        self.file_state.set_dirty()


class BoolTreeWidgetItem(OperationTreeWidgetItemBase):
    def __init__(self, file_state: FileStateContainer, variables: List[VariableDefinition], o: VariableOperation):
        super().__init__(file_state, variables, o)

        self.value_widget = QCheckBox()
        self.value_widget.setCheckState(o.value)

        self.value_widget.stateChanged.connect(self.on_check_box_value_changed)

    def on_check_box_value_changed(self, _: int) -> None:
        self.operation.value = self.value_widget.checkState()
        self.file_state.set_dirty()


class FloatTreeWidgetItem(OperationTreeWidgetItemBase):
    def __init__(self, file_state: FileStateContainer, variables: List[VariableDefinition], o: VariableOperation):
        super().__init__(file_state, variables, o)

        self.value_widget = QDoubleSpinBox()
        self.value_widget.setValue(o.value)

        self.value_widget.stateChanged.connect(self.on_spin_box_value_changed)

    def on_spin_box_value_changed(self, _: int) -> None:
        self.operation.value = self.value_widget.value()
        self.file_state.set_dirty()
