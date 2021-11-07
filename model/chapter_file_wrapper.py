import os

from model.generation import generate_new_chapter
from questlib import Chapter


class ChapterFileWrapper:
    ENCODING = 'utf-8'
    JSON_INDENT = 2

    def __init__(self, path: str):
        self._path = path
        self._file = open(self._path, 'r+', encoding=self.ENCODING)
        if os.path.getsize(self._path) > 0:
            self._data = Chapter.from_json(self._file.read())
        else:
            self._data = generate_new_chapter()
            self.save_changes()

    @property
    def data(self) -> Chapter:
        return self._data

    @property
    def path(self) -> str:
        return self._path

    def save_changes(self) -> None:
        self._file.seek(0)
        self._file.write(self._data.to_json(indent=self.JSON_INDENT, ensure_ascii=False))
        self._file.truncate()

    def close(self) -> None:
        self._file.close()
