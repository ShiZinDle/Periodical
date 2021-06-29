from typing import List
from pygame.rect import Rect
from pygame.surface import Surface

from periodical.config import (BLACK_FONT, CARD, CARD_BORDER, COLORS, FONT,
                               MEGA_CARD, Size, SMALL_FONT, SMALLER_FONT,
                               SMALLEST_FONT, WHITE_FONT, Zone)


class Card:
    """A class for representing card of elements of the periodic table.

    Attributes:
        name: Element's name.
        symbol: Element's symbol.
        number: Element's atomic number.
        mass: Element's rounded atomic mass.
        category: Element's categorical classification.
        zone: Card's current zone.
    """
    def __init__(self, name: str, symbol: str, number: int, mass: int,
                 category: str, shells: List[int], zone: Zone) -> None:
        self.name = name.title()
        self.symbol = symbol.title()
        self.number = number
        self.mass = round(mass)
        self.category = category.title()
        self.shells = shells
        self.zone = zone

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return (self.name == other.name
                and self.symbol == other.symbol
                and self.number == other.number
                and self.mass == other.mass
                and self.category == other.category
                and self.zone is other.zone)

    def __gt__(self, other: 'Card') -> bool:
        return self.number > other.number

    def render(self) -> None:
        """Creates an image of the card for pygame visualization."""
        self.rect = Rect((0, 0), CARD.size)
        card = border_and_fill(CARD, self.category, CARD_BORDER)

        center = card.get_rect().center
        centerx = card.get_rect().centerx

        symbol = FONT.render(self.symbol, *BLACK_FONT)
        symbol_pos = symbol.get_rect(center=center)
        number = FONT.render(str(self.number), *BLACK_FONT)
        number_pos = number.get_rect(
            centerx=centerx, centery=symbol_pos.top / 1.5)
        mass = FONT.render(str(self.mass), *WHITE_FONT)
        mass_pos = mass.get_rect(
            centerx=centerx, centery=(CARD.height - symbol_pos.bottom) * 2)

        for obj, pos in ((number, number_pos), (mass, mass_pos),
                         (symbol, symbol_pos)):
            card.blit(obj, pos)

        self.img = card

    def mega_render(self) -> None:
        """Creates a large image of the card for pygame visualization,
        including extra information."""
        self.rect = Rect((0, 0), MEGA_CARD.size)
        card = border_and_fill(MEGA_CARD, self.category, CARD_BORDER)

        rect = card.get_rect()
        row = {i: (rect.height / 6) * i for i in range(1, 7)}

        names_font = SMALLER_FONT if len(self.name) >= 11 else SMALL_FONT
        shells_font = SMALLEST_FONT if len(self.shells) >= 6 else SMALL_FONT

        number = FONT.render(str(self.number), *BLACK_FONT)
        number_pos = number.get_rect(centerx=rect.centerx, centery=row[1])
        symbol = FONT.render(self.symbol, *BLACK_FONT)
        symbol_pos = symbol.get_rect(centerx=rect.centerx, centery=row[2])
        name = names_font.render(self.name, *BLACK_FONT)
        name_pos = name.get_rect(centerx=rect.centerx, centery=row[3])
        mass = SMALL_FONT.render(str(self.mass), *WHITE_FONT)
        mass_pos = mass.get_rect(centerx=rect.centerx, centery=row[4])
        shells = shells_font.render(
            '-'.join([str(shell) for shell in self.shells]), *WHITE_FONT)
        shells_pos = shells.get_rect(centerx=rect.centerx, centery=row[5])

        for obj, pos in ((number, number_pos), (symbol, symbol_pos),
                         (name, name_pos), (mass, mass_pos),
                         (shells, shells_pos)):
            card.blit(obj, pos)

        self.img = card


def border_and_fill(size: Size, category: str, width: int = 0) -> Surface:
    """Returns the backround surface for a game object bordered and colored.

    Args:
        width: Outer border's size.
        size: Box size.
        category: Element's categorical classification.

    Returns:
        Background for a game object, colored and with outer border.
    """
    if width < 0:
        width = 0
    border_size = border_width, border_height = width, width
    card = Surface(size.size).convert()
    background = Surface((size.width - border_width * 2,
                          size.height - border_height * 2)).convert()
    background.fill(COLORS[category])
    card.blit(background, border_size)
    return card
