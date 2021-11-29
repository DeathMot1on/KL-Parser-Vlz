from datetime import datetime
from dataclasses import dataclass

@dataclass
class Article:
    title: str
    category: str
    date: datetime
    link: str
    text: str
    videos: list
    photos: list
    comments_count: int = 0

    def __getitem__(self, key):
        return super().__getattribute__(key)