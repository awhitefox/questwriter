from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox


class BoolComboBox(QComboBox):
    value_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.addItems(['False', 'True'])
        self.currentIndexChanged.connect(self._on_current_index_changed)

    @property
    def value(self) -> bool:
        return bool(self.currentIndex())

    @value.setter
    def value(self, value: bool) -> None:
        value = int(value)
        if value != self.currentIndex():
            self.setCurrentIndex(value)
            # noinspection PyUnresolvedReferences
            self.value_changed.emit(value)

    def _on_current_index_changed(self, index: int):
        # noinspection PyUnresolvedReferences
        self.value_changed.emit(bool(index))
