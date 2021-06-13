from abc import ABC
import json
from random import shuffle
from typing import Any, List, Optional, Tuple

from periodical.card import Card, move_zone
from periodical.config import *


def get_cards(path: str) -> List[Card]:
    with open(path, 'r',encoding='utf-8') as file_handler:
        file = file_handler.read()
    elements = json.loads(file)['elements']
    cards = [Card(element['name'], element['symbol'], element['number'],
                  round(element['atomic_mass']), element['category'],
                  Zone.LIMBO)
             for element in elements
             if element['number'] <= ELEMENTS_AMOUNT]
    return cards


def generate_cards(*, first: Optional[int] = None,
                   last: Optional[int] = None) -> List[Card]:
    cards = get_cards(PATH)
    if not first:
        first = 0
    if not last:
        last = len(cards)
    cards =  cards.copy()[first:last]
    return cards


class Deck(ABC):
    def __init__(self, zone: Zone, *cards: Tuple[Card, ...],
                 **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self._cards = list(cards)
        move_zone(zone, self._cards)

    def __bool__(self) -> bool:
        return len(self._cards) != 0

    def __len__(self) -> int:
        return len(self._cards)

    def __eq__(self, other: Any) -> bool:
        return sorted(self._cards) == sorted(other._cards)

    def draw(self) -> Optional[Card]:
        try:
            return self._cards.pop(0)
        except IndexError:
            return None

    def shuffle(self) -> None:
        shuffle(self._cards)


class StartingDeck(Deck):
    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(Zone.PLAYER_DECK, *generate_cards(last=10),
                         *args, **kwargs)


class LightDeck(Deck):
    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(Zone.LIGHT_DECK, *generate_cards(first=2, last=18),
                         *args, **kwargs)


class HeavyDeck(Deck):
    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(Zone.HEAVY_DECK, *generate_cards(first=18),
                         *args, **kwargs)