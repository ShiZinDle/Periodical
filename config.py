from enum import Enum
from typing import Any, List, Tuple, Union

import pygame
from pygame.font import Font
from pygame.rect import Rect
from pygame.surface import Surface

pygame.init()

NUM = Union[int, float]
CARD_IMG = List[Tuple[Surface, Rect]]

MIN_PLAYER_AMOUNT = 1
ELEMENTS_AMOUNT = 118
LIGHT_AMOUNT = 4
HEAVY_AMOUNT = 2
LIGHT_START = 3
LIGHT_END = 18
GENERAL_END = 2
LIGHT_DECK_LIMIT = 3
HEAVY_DECK_LIMIT = 5
PATH = 'D:\\Yuval\\Game Design\\Periodical\\Source Material\\elements.json'
COLORS = {
    'Reactive Nonmetal': (8, 163, 21),
    'Noble Gas': (255, 115, 201),
    'Alkali Metal': (145, 3, 3),
    'Alkaline Earth Metal': (214, 149, 9),
    'Metalloid': (128, 55, 68),
    'Post Transition Metal': (108, 179, 212),
    'Transition Metal': (130, 10, 209),
    'Lanthanide': (40, 61, 224),
    'Actinide': (204, 82, 0),
    'Unknown': (150, 150, 150),
    'discard': (240, 81, 2),
    'hand': (92, 0, 92),
    'lab': (0, 245, 233),
    'market': (42, 163, 53),
    'table': (230, 7, 14),
    'button_area': (138, 0, 96),
    'end_turn': (150, 0, 20),
    'mulligan': (76, 189, 237),
    'energy': (49, 224, 142),
}


class Size:
    """A class for representing the size of a rectangle.

    Attributes:
        width: Rectangle's width.
        height: Rectangle's height.
        size: Rectangle's width and height.
    """
    def __init__(self, width: Union[int, float], height: Union[int, float],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)  # type: ignore
        self.width = width
        self.height = height
        self.size = width, height


class Pos:
    """A class for representing the position of a rectangle on a surface.

    Attributes:
        x: Rectangle's x position.
        y: Rectangle's y position.
        pos: Rectangle's x and y positions.
    """
    def __init__(self, x: Union[int, float], y: Union[int, float],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)  # type: ignore
        self.x = x
        self.y = y
        self.pos = x, y


class Board(Size, Pos):
    """A class for representing the size of a rectangle and its position on a
    surface."""
    pass


CARD = Size(width=75, height=100)
MEGA_CARD = Size(width=CARD.width * 1.35, height=CARD.height * 1.35)
SPACE = CARD.width / 5
main_width = int(CARD.width * 5 + SPACE * 6)
main_height = int(CARD.height * 2 + SPACE * 3)
side_width = int(CARD.height + SPACE * 2)
button_area_height = CARD.height
SCREEN = Size(width=main_width + side_width * 3,
              height=main_height * 2 + button_area_height)
LAB = Board(width=side_width, height=SCREEN.height, x=0, y=0)
MARKET = Board(width=main_width, height=main_height,
               x=side_width, y=0)
HAND = Board(width=main_width, height=main_height,
             x=side_width, y=main_height)
TABLE = Board(width=side_width, height=SCREEN.height,
              x=main_width + side_width, y=0)
DISCARD = Board(width=side_width, height=SCREEN.height,
                x=main_width + side_width * 2, y=0)
BUTTON_AREA = Board(width=main_width, height=button_area_height,
                    x=side_width, y=SCREEN.height - button_area_height)

BUTTON = Size(width=CARD.width * 2.5, height=CARD.height / 2)
button_height = SCREEN.height - BUTTON.height
button_space = (main_width - BUTTON.width * 2) / 3
ENERGY = Pos(x=side_width + main_width - BUTTON.width / 2 - button_space,
             y=button_height)
END_TURN = Pos(x=side_width + BUTTON.width / 2 + button_space,
               y=button_height)

BUTTON_BORDER = 5
CARD_BORDER = 3

FONT = Font(None, 36)
SMALL_FONT = Font(None, 22)
SMALLER_FONT = Font(None, 20)
SMALLEST_FONT = Font(None, 17)
BLACK_FONT = (True, (10, 10, 10))
WHITE_FONT = (True, (245, 245, 245))


class Zone(Enum):
    """A class for card location indication."""
    LIMBO = 0
    PLAYER_DECK = 1
    HAND = 2
    TABLE = 3
    DISCARD = 4
    LAB = 5
    GENERAL_MARKET = 6
    LIGHT_DECK = 7
    HEAVY_DECK = 8
    LIGHT_MARKET = 9
    HEAVY_MARKET = 10
