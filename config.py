from enum import Enum
from typing import Any, Dict, Tuple

ELEMENTS_AMOUNT = 118
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
    def __init__(self, width: int, height: int, *args: Tuple[Any],
                 **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.size = width, height


class Pos:
    def __init__(self, x: int, y: int, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.pos = x, y


class Board(Size, Pos):
    def __init__(self, width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)


SCREEN = Size(1000, 1000)
center_width = 650
button_area_height = 100
center_height = (SCREEN.height - button_area_height) / 3
side_width = (SCREEN.width - center_width) / 2
DISCARD = Board(side_width, SCREEN.height, 0, 0)
MARKET = Board(center_width, center_height, DISCARD.width, 0)
TABLE = Board(center_width, center_height, DISCARD.width, center_height)
HAND = Board(center_width, center_height, DISCARD.width, center_height * 2)
LAB = Board(side_width, SCREEN.height, SCREEN.width - side_width, 0)
BUTTON_AREA = Board(center_width, button_area_height,
                    DISCARD.width, SCREEN.height - button_area_height)

CARD = Size(100, 125)
SYMBOL_HEIGHT = 30
BUTTON = Size(200, 50)
button_height = SCREEN.height - 50
button_width =  12.5
ENERGY = Pos(LAB.x - BUTTON.width / 2 - button_width, button_height)
END_TURN = Pos(DISCARD.width + BUTTON.width / 2 + button_width, button_height)
MULLIGAN = Pos(END_TURN.x + BUTTON.width + button_width, button_height)

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