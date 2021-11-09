from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal


class FileState(Enum):
    CLEAN = 0
    DIRTY = 1


class FileStateContainer(QObject):
    state_changed = pyqtSignal(FileState)

    def __init__(self, value: FileState = FileState.CLEAN):
        super().__init__()
        self._value = value

    @property
    def value(self) -> FileState:
        return self._value

    def set_clean(self):
        self._set_value(FileState.CLEAN)

    def set_dirty(self):
        self._set_value(FileState.DIRTY)

    def _set_value(self, value: FileState) -> None:
        if self._value != value:
            self._value = value
            # noinspection PyUnresolvedReferences
            self.state_changed.emit(value)
