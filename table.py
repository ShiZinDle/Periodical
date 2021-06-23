from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import pygame
from pygame.constants import KEYDOWN, K_ESCAPE, QUIT
from pygame.font import Font
from pygame.surface import Surface

from periodical.card import border_and_fill
from periodical.config import BLACK_FONT, PATH, Size
from periodical.utils import get_element_info


ELEMENT = Size(width=40, height=50)
AROUND = 10
TABLE = Size(width=ELEMENT.width * 18 + AROUND,
             height=ELEMENT.height * 10 + AROUND)
FONT = Font(None, 24)
SMALL_FONT = Font(None, 22)
SMALLER_FONT = Font(None, 17)
BORDER = 1
MAX_NUM_RANGE = 5


class Cell(ABC):
    '''A class for representing a cell of the periodic table.

    Attributes:
        group: Element's group.
        period: Element's period.
        category: Element's categorical classification.
    '''
    def __init__(self, group: int, period: int, category: str) -> None:
        self.group = group - 1
        self.period = period - 1
        self.category = category.title()

    def position(self) -> Tuple[int, int]:
        '''Return position of cell on the periodic table.

        Returns:
            Position of cell on the periodic table.
        '''
        x = y = AROUND / 2
        x_addition = y_addition = 0
        if self.group != 0:
            x_addition = BORDER
        if self.period != 0:
            y_addition = BORDER
        return (int((ELEMENT.width - x_addition) * (self.group) + x),
                int((ELEMENT.height - y_addition) * (self.period) + y))

    @abstractmethod
    def show(self) -> Surface: pass
    '''Return an image of the cell to be printed to the screen.'''


class Element(Cell):
    '''A class for representing an element of the periodic table.

    Attributes:
        name: Element's name.
        symbol: Element's symbol.
        number: Element's atomic number.
        group: Element's group.
        period: Element's period.
        category: Element's categorical classification.
    '''
    def __init__(self, name: str, symbol: str, number: int, group: int,
                 period: int, category: str) -> None:
        super().__init__(group, period, category)
        self.name = name.title()
        self.symbol = symbol.title()
        self.number = str(number)

    def show(self) -> Surface:
        element = border_and_fill(ELEMENT, self.category, BORDER)
        centerx = element.get_rect().centerx
        number = FONT.render(self.number, *BLACK_FONT)
        number_pos = number.get_rect(centerx=centerx,
                                     centery=element.get_height() / 3)
        symbol = FONT.render(self.symbol, *BLACK_FONT)
        symbol_pos = symbol.get_rect(centerx=centerx,
                                     centery=element.get_height() / 3 * 2)

        for img, pos in ((number, number_pos), (symbol, symbol_pos)):
            element.blit(img, pos)

        return element


class ElementGroup(Cell):
    '''A class for representing a group of elements of the periodic table.

    Attributes:
        first: Atomic number of first element in group.
        last: Atomic number of last element in group.
        group: Element group's group (column) on the periodic table.
        period: Element group's period.
        category: Element group's categorical classification.
    '''
    def __init__(self, first: int, last: int, group: int, period: int,
                 category: str) -> None:
        super().__init__(group, period, category)
        self.first = first
        self.last = last

    def show(self) -> Surface:
        group = border_and_fill(ELEMENT, self.category, BORDER)
        font = SMALL_FONT
        num_range = f'{self.first}-{self.last}'
        if len(num_range) > MAX_NUM_RANGE:
            font = SMALLER_FONT
        number = font.render(num_range, *BLACK_FONT)
        number_pos = number.get_rect(center=group.get_rect().center)

        group.blit(number, number_pos)

        return group


def create_elements(elements: List[Dict[str, Any]]) -> List[Element]:
    '''Return list of cards based on the passed elements and the given range.

    Args:
        elements: Complete details of each element.
        first: Number of first element to create a card for.
        last: Number of last element to create a card for.

    Returns:
        List of cards each depicting a unique element.
    '''
    return [Element(element['name'], element['symbol'], element['number'],
                    element['xpos'], element['ypos'], element['category'])
            for element in elements]


def show_table(cells: List[Cell]) -> None:
    '''Print an image of the periodic table to the screen.

    Args:
        cells: Details of all cells to print.
    '''
    screen = pygame.display.set_mode(TABLE.size)  # type: ignore
    screen.fill((250, 250, 250))
    pygame.display.set_caption('Periodical')

    while True:
        for event in pygame.event.get():
            if (event.type == QUIT or event.type == KEYDOWN
                    and event.key == K_ESCAPE):
                return

        for cell in cells:
            screen.blit(cell.show(), cell.position())

        pygame.display.flip()


if __name__ == '__main__':
    elements: List[Cell] = []
    elements.extend(create_elements(get_element_info(PATH)[:-1]))
    elements.append(ElementGroup(57, 71, 3, 6, 'lanthanide'))
    elements.append(ElementGroup(89, 103, 3, 7, 'actinide'))
    show_table(elements)
