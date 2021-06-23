from pygame.rect import Rect
from pygame.surface import Surface

from periodical.config import (BLACK_FONT, CARD, CARD_BORDER, COLORS, FONT,
                               Size, WHITE_FONT, Zone)


class Card:
    '''A class for representing card of elements of the periodic table.

    Attributes:
        name: Element's name.
        symbol: Element's symbol.
        number: Element's atomic number.
        mass: Element's rounded atomic mass.
        category: Element's categorical classification.
        zone: Card's current zone.

    '''
    def __init__(self, name: str, symbol: str, number: int,
                 mass: int, category: str, zone: Zone) -> None:
        self.name = name.title()
        self.symbol = symbol.title()
        self.number = number
        self.mass = mass
        self.category = category.title()
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
        '''Create an image of the card for pygame visualization.'''
        self.rect = Rect((0, 0), CARD.size)
        card = border_and_fill(CARD_BORDER, CARD, self.category)

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


def border_and_fill(width: int, size: Size, category: str) -> Surface:
    '''Return the backround border and color for a game object.

    Args:
        width: Outer border's size.
        size: Box size.
        category: Element's categorical classification.

    Returns:
        Background for a game object, colored and with outer border.
        '''
    border_size = border_width, border_height = width, width
    card = Surface(size.size).convert()
    background = Surface((size.width - border_width * 2,
                          size.height - border_height * 2)).convert()
    background.fill(COLORS[category])
    card.blit(background, border_size)
    return card
