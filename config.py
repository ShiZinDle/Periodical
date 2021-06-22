from enum import Enum
from typing import Any, List, Tuple, Union

from pygame.rect import Rect
from pygame.surface import Surface

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
    'Lanthanide': (29, 49, 204),
    'Actinide': (204, 82, 0),
    'Unknown': (181, 181, 181),
    'discard': (240, 81, 2),
    'hand': (92, 0, 92),
    'lab': (0, 245, 233),
    'market': (42, 163, 53),
    'table': (230, 7, 14),
    'button_area': (138, 0, 96),
    'end_turn': (150, 0, 20),
    'mulligan': (19, 0, 166),
    'energy': (99, 255, 182),
}


class Size:
    def __init__(self, width: Union[int, float], height: Union[int, float],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)  # type: ignore
        self.width = width
        self.height = height
        self.size = width, height


class Pos:
    def __init__(self, x: Union[int, float], y: Union[int, float],
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)  # type: ignore
        self.x = x
        self.y = y
        self.pos = x, y


class Board(Size, Pos):
    pass


SCREEN = Size(width=1000, height=1000)
center_width = 650
button_area_height = 100
center_height = (SCREEN.height - button_area_height) / 3
side_width = (SCREEN.width - center_width) / 2
DISCARD = Board(width=side_width, height=SCREEN.height, x=0, y=0)
TABLE = Board(width=center_width, height=center_height, x=DISCARD.width, y=0)
MARKET = Board(width=center_width, height=center_height,
               x=DISCARD.width, y=center_height)
HAND = Board(width=center_width, height=center_height,
             x=DISCARD.width, y=center_height * 2)
LAB = Board(width=side_width, height=SCREEN.height,
            x=SCREEN.width - side_width, y=0)
BUTTON_AREA = Board(width=center_width, height=button_area_height,
                    x=DISCARD.width, y=SCREEN.height - button_area_height)

CARD = Size(width=100, height=125)
SYMBOL_HEIGHT = 30
BUTTON = Size(width=200, height=50)
button_height = SCREEN.height - 50
button_width = 12.5
ENERGY = Pos(x=LAB.x - BUTTON.width / 2 - button_width, y=button_height)
END_TURN = Pos(x=DISCARD.width + BUTTON.width / 2 + button_width,
               y=button_height)
MULLIGAN = Pos(x=END_TURN.x + BUTTON.width + button_width, y=button_height)

BUTTON_BORDER = 5
CARD_BORDER = 3


class Zone(Enum):
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
