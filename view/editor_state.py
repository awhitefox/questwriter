from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from questlib import Branch, Segment, Option

from observable_property import ObservableProperty


class _EditorState(QObject):
    current_branch_changed = pyqtSignal(object)
    current_segment_changed = pyqtSignal(object)
    current_option_changed = pyqtSignal(object)

    current_branch: Optional[Branch] = ObservableProperty('current_branch_changed')
    current_segment: Optional[Segment] = ObservableProperty('current_segment_changed')
    current_option: Optional[Option] = ObservableProperty('current_option_changed')

    def __init__(self):
        super().__init__()
        self.current_branch = None
        self.current_segment = None
        self.current_option = None


EditorState = _EditorState()
