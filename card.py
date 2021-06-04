from typing import Any


class Card:
    def __init__(self, name: str, symbol: str, number: int,
                 mass: int, category: str) -> None:
        self.name = name.title()
        self.symbol = symbol.title()
        self.number = number
        self.mass = mass
        self.category = category.title()

    def __str__(self) -> str:
        max_len = max(len(self.name), len(self.category))
        card = str(self.number)
        r = (max_len
             - len(str(self.number))
             - len(self.symbol)
             - len(str(self.mass))
             ) // 2
        r = max(2, r)
        for i in (self.symbol, str(self.mass)):
            for _ in range(r):
                card += ' '
            card += i
        card += '\n' + self.name
        card += '\n' + self.category
        return card + '\n'

    def __eq__(self, other: Any) -> bool:
        return (self.name == other.name
                and self.symbol == other.symbol
                and self.number == other.number
                and self.mass == other.mass
                and self.category == other.category)

    def __gt__(self, other) -> bool:
        return self.number > other.number