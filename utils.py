from typing import List, Callable, Optional, TypeVar
T = TypeVar('T')


def find(elements: List[T], predicate: Callable[[T], bool], fallback: Optional[T] = None) -> Optional[T]:
    for elem in elements:
        if predicate(elem):
            return elem
    return fallback


def find_index(elements: List[T], predicate: Callable[[T], bool], fallback: Optional[int] = None) -> Optional[int]:
    for i, elem in enumerate(elements):
        if predicate(elem):
            return i
    return fallback
