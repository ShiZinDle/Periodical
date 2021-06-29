from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import pygame
from pygame.constants import KEYDOWN, K_ESCAPE, QUIT
from pygame.font import Font
from pygame.rect import Rect
from pygame.surface import Surface

from periodical.card import border_and_fill, Card
from periodical.config import (BLACK_FONT, Board, MEGA_CARD, NUM, PATH, Size,
                               SMALL_FONT, SMALLER_FONT, SMALLEST_FONT,
                               WHITE_FONT, Zone)
from periodical.utils import get_element_info


CELL = Size(width=40, height=50)
SHELL = Size(width=CELL.width, height=80)
AROUND = 10
BORDER = 1
GROUPS = 18
ADDITIONAL_GROUPS = 14
PERIODS = 10
ADDITIONAL_PERIODS = 3
FONT = Font(None, 24)
MAX_NUM_RANGE = 5
CARD_COL = 7
CARD_COL_ADDITION = 2
BUTTON_GROUP = 12
LANTHANIDES = 57, 71, 3, 6, 'lanthanide'
ACTINIDES = 89, 103, 3, 7, 'actinide'


class Cell(ABC):
    """A class for representing a cell of the periodic table.

    Attributes:
        group: Element's group.
        period: Element's period.
        category: Element's categorical classification.
    """
    def __init__(self, group: int, period: int, category: str) -> None:
        self.group = group - 1
        self.period = period - 1
        self.category = category.title()

    def get_rect(self, shells: bool) -> Rect:
        """Returns a Rect object containing the size and position of the cell
        on the periodic table.

        Args:
            shells: Determines the size of the cells on the table, and their
                    corresponding position.

        Returns:
            Rect object containing the size and position of the cell on the
            periodic table.
        """
        size, group, period = CELL, self.group, self.period
        if shells:
            size = SHELL
            if period > 7:
                period -= 3
            elif group > 2:
                group += 14
        addition = AROUND / 2
        x_addition = y_addition = 0
        if self.group != 0:
            x_addition = BORDER
        if self.period != 0:
            y_addition = BORDER

        return Rect((int((size.width - x_addition) * (group)
                         + addition),
                     int((size.height - y_addition) * (period)
                         + addition)),
                    size.size)

    @abstractmethod
    def show(self) -> Surface: pass
    """Returns an image of the cell to be printed to the screen."""

    @abstractmethod
    def show_shells(self) -> Surface: pass
    """Returns a large image of the cell to be printed to the screen."""

    def render(self) -> None:
        """Create cell image and get its target position."""
        self.img = self.show()
        self.shell_img = self.show_shells()
        self.pos = self.get_rect(False)
        self.shell_pos = self.get_rect(True)


class Element(Cell):
    """A class for representing an element of the periodic table.

    Attributes:
        name: Element's name.
        symbol: Element's symbol.
        number: Element's atomic number.
        card: Card representation of element.
        group: Element's group.
        period: Element's period.
        category: Element's categorical classification.
    """
    def __init__(self, name: str, symbol: str, number: int, group: int,
                 period: int, category: str, mass: int,
                 shells: List[int]) -> None:
        super().__init__(group, period, category)
        self.name = name.title()
        self.symbol = symbol.title()
        self.number = str(number)
        self.card = Card(name, symbol, number, mass,
                         category, shells, Zone.LIMBO)

    def show(self) -> Surface:
        """Returns an image of the element to be printed to the screen.

        Returns:
            Image of the element to be printed to the screen.
        """
        element = border_and_fill(CELL, self.category, BORDER)
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

    def show_shells(self) -> Surface:
        """Returns a large image of the element to be printed to the screen.

        Returns:
            Large image of the element to be printed to the screen.
        """
        element = border_and_fill(SHELL, self.category, BORDER)
        shells = self.card.shells
        length = len(shells) + 2
        rect = element.get_rect()
        row = {i: (rect.height / length) * i for i in range(1, length)}
        number = SMALLER_FONT.render(str(self.number), *WHITE_FONT)
        num_pos = number.get_rect(centerx=rect.centerx, centery=row[1])
        element.blit(number, num_pos)
        for i, shell in enumerate(shells, start=2):
            text = SMALLEST_FONT.render(str(shell), *BLACK_FONT)
            pos = text.get_rect(centerx=rect.centerx, centery=row[i])
            element.blit(text, pos)

        return element


class ElementGroup(Cell):
    """A class for representing a group of elements of the periodic table.

    Attributes:
        first: Atomic number of first element in group.
        last: Atomic number of last element in group.
        group: Element group's group (column) on the periodic table.
        period: Element group's period.
        category: Element group's categorical classification.
    """
    def __init__(self, first: int, last: int, group: int, period: int,
                 category: str) -> None:
        super().__init__(group, period, category)
        self.first = first
        self.last = last

    def show(self, size: Size = CELL) -> Surface:
        """Returns an image of the cell to be printed to the screen.

        Args:
            size: Cell's size.

        Returns:
            Image of the cell to be printed to the screen.
        """
        group = border_and_fill(size, self.category, BORDER)
        font = SMALL_FONT
        num_range = f'{self.first}-{self.last}'
        if len(num_range) > MAX_NUM_RANGE:
            font = SMALLEST_FONT
        number = font.render(num_range, *BLACK_FONT)
        number_pos = number.get_rect(center=group.get_rect().center)

        group.blit(number, number_pos)

        return group

    def show_shells(self) -> Surface:
        """Returns a large image of the cell to be printed to the screen.

        Returns:
            Large image of the element to be printed to the screen.
        """
        return self.show(SHELL)


def create_elements(elements: List[Dict[str, Any]]) -> List[Element]:
    """Returns list of cells based on the passed element details.

    Args:
        elements: Complete details of each element.

    Returns:
        List of cells each depicting a unique element.
    """
    return [Element(element['name'], element['symbol'], element['number'],
                    element['xpos'], element['ypos'], element['category'],
                    element['atomic_mass'], element['shells'])
            for element in elements]


def get_element_collision(cells: List[Cell], pos: Tuple[int, int],
                          shells: bool) -> Optional[Element]:
    """Checks for mouse collision with cells and returns relevant cell if
    collision occurres.

    Args:
        cells: List of all cells.
        pos: Mouse position.
        shells: Determines the size of the cells on the table, and their
                corresponding position.

    Returns:
        Cell with which mouse collided, if exists.
    """
    for cell in cells:
        if isinstance(cell, Element):
            if shells:
                rect = cell.shell_pos
            else:
                rect = cell.pos
            if rect.collidepoint(pos):
                return cell
    return None


def get_screen(shells: bool) -> Surface:
    """Returns surface object representing the screen.

    Args:
        shells: Determines the size of the cells on the table, and their
                corresponding position.

    Returns:
        Surface object representing the screen.
    """
    size, groups, periods = CELL, GROUPS, PERIODS

    if shells:
        size = SHELL
        groups += ADDITIONAL_GROUPS
        periods -= ADDITIONAL_PERIODS
    screen = pygame.display.set_mode((
        ((size.width - BORDER) * (groups - 1) + size.width  # type: ignore
         + AROUND),
        (size.height - BORDER) * (periods - 1) + size.height + AROUND))
    screen.fill((250, 250, 250))
    return screen


def get_button(shells: bool) -> Board:
    """Returns button size and position.

    Args:
        shells: Determines the size of the cells on the table, and their
                corresponding position.

    Returns:
        Button size and position.
    """
    size, pos = CELL, BUTTON_GROUP
    if shells:
        size = SHELL
        pos += ADDITIONAL_GROUPS
    return Board(width=size.width * 4 - BORDER * 3, height=size.height,
                 x=int((size.width - BORDER) * pos + AROUND / 2), y=AROUND / 2)


def show_mode_button(screen: Surface, shells: bool) -> None:
    """Creates mode changing button and pastes it to the screen.

    Args:
        screen: Surface object onto which to paste the button.
        shells: Determines the size of the cells on the table, and their
                corresponding position.
    """
    if shells:
        message = 'VIEW ELEMENT DETAILS'
    else:
        message = 'VIEW VALANCE SHELLS'
    button = border_and_fill(get_button(shells), 'mulligan', BORDER)
    text = Font(None, 18).render(message, *BLACK_FONT)
    text_pos = text.get_rect(center=button.get_rect().center)
    button.blit(text, text_pos)
    button_size = get_button(shells)
    button_pos = button.get_rect(left=button_size.x, top=button_size.y)
    screen.blit(button, button_pos)


def get_mega_card_pos(shells: bool) -> Tuple[NUM, NUM]:
    """Returns position of large card, showing extra details on the element.

    Args:
        shells: Determines the size of the cells on the table, and their
                corresponding position.

    Returns:
        Large detailed card's position on the screen.
    """
    col = CARD_COL
    row: NUM = AROUND
    if shells:
        col += CARD_COL_ADDITION
        row += SHELL.height * 1.5
    return ((CELL.width - BORDER) * (col - 1.5) + CELL.width
            - MEGA_CARD.width / 2 + AROUND / 2, row)


def show_table(cells: List[Cell]) -> None:
    """Prints an image of the periodic table to the screen.

    Args:
        cells: Details of all cells to print.
    """
    shells = False
    screen = get_screen(shells)
    pygame.display.set_caption('Periodical')

    for cell in cells:
        cell.render()

    while True:
        for event in pygame.event.get():
            if (event.type == QUIT or event.type == KEYDOWN
                    and event.key == K_ESCAPE):
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    button = get_button(shells)
                    if Rect(button.pos, button.size).collidepoint(event.pos):
                        if shells:
                            shells = False
                            screen = get_screen(shells)
                        else:
                            shells = True
                            screen = get_screen(shells)
                    element = get_element_collision(cells, event.pos, shells)
                    if element:
                        element.card.mega_render()
                        screen.blit(element.card.img,
                                    get_mega_card_pos(shells))

        for cell in cells:
            img, pos = cell.img, cell.pos
            if shells:
                img = cell.shell_img
                pos = cell.shell_pos
            screen.blit(img, pos)

        show_mode_button(screen, shells)
        pygame.display.flip()


if __name__ == '__main__':
    elements: List[Cell] = []
    elements.extend(create_elements(get_element_info(PATH)[:-1]))
    elements.append(ElementGroup(*LANTHANIDES))
    elements.append(ElementGroup(*ACTINIDES))
    show_table(elements)
