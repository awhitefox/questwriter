import os
import json

from model.generation import generate_new_chapter


class ChapterFileWrapper:
    ENCODING = 'utf-8'
    JSON_INDENT = 2

    def __init__(self, path: str):
        self._path = path
        self._file = open(self._path, 'r+', encoding=self.ENCODING)
        if os.path.getsize(self._path) > 0:
            self._data = json.load(self._file)
        else:
            self._data = generate_new_chapter()
            self.save_changes()

    @property
    def data(self) -> dict:
        return self._data

    @property
    def path(self) -> str:
        return self._path

    def save_changes(self) -> None:
        self._file.seek(0)
        json.dump(self._data, self._file, indent=self.JSON_INDENT, ensure_ascii=False)
        self._file.truncate()

    def close(self) -> None:
        self._file.close()
