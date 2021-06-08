from typing import Any

import pygame

from periodical.config import COLORS


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

    def __gt__(self, other: Any) -> bool:
        return self.number > other.number

    def compare(self, number: int) -> bool:
        return self.number == number

    def render(self) -> pygame.Surface:
        size = width, height = 100, 125
        top = 15
        border_size = border_width, border_height = 3, 3

        font = pygame.font.Font(None, 42)
        black_font = (1, (10, 10, 10))
        white_font = (1, (245, 245, 245))

        border = pygame.Surface(size).convert()
        background = pygame.Surface((
            width - border_width * 2, height - border_height * 2)).convert()
        background.fill(COLORS[self.category])
        border.blit(background, border_size)
        center = border.get_rect().center
        centerx = border.get_rect().centerx

        symbol = font.render(self.symbol, *black_font)
        symbol_pos = symbol.get_rect(center=center)
        number = font.render(str(self.number), *black_font)
        number_pos = number.get_rect(
            centerx=centerx, top=symbol.get_height() - top)
        mass = font.render(str(self.mass), *white_font)
        mass_pos = mass.get_rect(
            centerx=centerx, top=height - (symbol.get_height() + top))

        for obj, pos in ((number, number_pos), (mass, mass_pos),
                        (symbol, symbol_pos)):
            border.blit(obj, pos)

        white_font = (1, (250, 250, 250))

        return border
