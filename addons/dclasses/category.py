from dataclasses import dataclass

@dataclass
class Category:
    title: str
    index: int
    path: str

    def __getitem__(self, key):
        return super().__getattribute__(key)