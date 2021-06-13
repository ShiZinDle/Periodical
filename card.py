from config import Board, CARD_BORDER, Size
from typing import Any, List, Tuple

from pygame import Rect, Surface
from pygame.font import Font

from periodical.config import CARD, COLORS, SYMBOL_HEIGHT, Zone


class Card:
    def __init__(self, name: str, symbol: str, number: int,
                 mass: int, category: str, zone: Zone) -> None:
        self.name = name.title()
        self.symbol = symbol.title()
        self.number = number
        self.mass = mass
        self.category = category.title()
        self.zone = zone

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
                and self.category == other.category
                and self.zone is other.zone)

    def __gt__(self, other: Any) -> bool:
        return self.number > other.number

    def compare(self, number: int) -> bool:
        return self.number == number

    def render(self) -> None:
        self.rect = Rect((0, 0), CARD.size)
        top = 15
        card = border_and_fill(CARD_BORDER, CARD, self.category)

        font = Font(None, 42)
        black_font = (1, (10, 10, 10))
        white_font = (1, (245, 245, 245))

        center = card.get_rect().center
        centerx = card.get_rect().centerx

        symbol = font.render(self.symbol, *black_font)
        symbol_pos = symbol.get_rect(center=center)
        number = font.render(str(self.number), *black_font)
        number_pos = number.get_rect(
            centerx=centerx, top=SYMBOL_HEIGHT - top)
        mass = font.render(str(self.mass), *white_font)
        mass_pos = mass.get_rect(centerx=centerx,
                                 top=CARD.height - (SYMBOL_HEIGHT + top))

        for obj, pos in ((number, number_pos), (mass, mass_pos),
                        (symbol, symbol_pos)):
            card.blit(obj, pos)

        self.img = card

    def calc_surface_heights(board: Board) -> Tuple[int, int]:
        return ((board.height / 2 - CARD.height) / 2,
                (board.height * 2 - CARD.height) / 3)


def move_zone(zone: Zone, cards: List[Card]) -> None:
    for card in cards:
        card.zone = zone


def border_and_fill(girth: int, size: Size, category: str):
    border_size = border_width, border_height = girth, girth
    card = Surface(size.size).convert()
    background = Surface((size.width - border_width * 2,
                            size.height - border_height * 2)).convert()
    background.fill(COLORS[category])
    card.blit(background, border_size)
    return card