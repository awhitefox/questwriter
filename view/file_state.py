from PyQt5.QtCore import QObject, pyqtSignal


class _FileState(QObject):
    state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._is_dirty = False

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    def set_clean(self):
        self._set_dirty(False)

    def set_dirty(self):
        self._set_dirty(True)

    def _set_dirty(self, value: bool) -> None:
        if self._is_dirty != value:
            self._is_dirty = value
            # noinspection PyUnresolvedReferences
            self.state_changed.emit(value)


FileState = _FileState()
