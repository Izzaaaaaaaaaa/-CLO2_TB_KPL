# entities.py
from typing import List
from pydantic import BaseModel

class Film(BaseModel):
    judul: str
    genre: str
    durasi: str
    rating: str
    teater: str
    jadwal: List[str]
    harga_tiket: int
