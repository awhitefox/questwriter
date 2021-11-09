from PyQt5.QtWidgets import QTreeWidgetItem

from typing import List


def tree_widget_item_indexes(item: QTreeWidgetItem) -> List[int]:
    result = []
    while True:
        p = item.parent()
        if p is None:
            break
        result.insert(0, p.indexOfChild(item))
        item = p
    return result
