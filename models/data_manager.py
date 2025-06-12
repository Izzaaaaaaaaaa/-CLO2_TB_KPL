# data_manager.py
from typing import TypeVar, Generic, List

T = TypeVar('T')

class DataManager(Generic[T]):
    def __init__(self):
        self.data: List[T] = []

    def tambah(self, item: T):
        self.data.append(item)

    def ambil_semua(self) -> List[T]:
        return self.data

    def cari(self, key: str, value: str) -> List[T]:
        return [item for item in self.data if getattr(item, key, None) == value]
