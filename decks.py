from abc import ABC
import json
from random import shuffle
from typing import List, Optional, Tuple

from periodical.card import Card


ELEMENTS_AMOUNT = 118


def get_cards(path: str) -> List[Card]:
    with open(path, 'r',encoding='utf-8') as file_handler:
        file = file_handler.read()
    elements = json.loads(file)['elements']
    cards = [Card(element['name'], element['symbol'], element['number'],
                  round(element['atomic_mass']), element['category'])
             for element in elements
             if element['number'] <= ELEMENTS_AMOUNT]
    return cards

CARDS = get_cards('D:\\Yuval\\Game Design\\Periodic Table Game\\Source Material\\elements.json')


class Deck(ABC):
    def __init__(self, *cards: Tuple[Card], **kwargs) -> None:
        super().__init__(**kwargs)
        self._cards = list(cards)

    def __bool__(self) -> bool:
        return len(self._cards) != 0

    def __len__(self) -> int:
        return len(self._cards)

    def draw(self) -> Optional[Card]:
        try:
            return self._cards.pop(0)
        except IndexError:
            return None

    def shuffle(self) -> None:
        shuffle(self._cards)


class StartingDeck(Deck):
    def __init__(self, **kwargs) -> None:
        super().__init__(*CARDS[:10], **kwargs)


class LightDeck(Deck):
    def __init__(self, **kwargs) -> None:
        super().__init__(*CARDS[2:18], **kwargs)


class HeavyDeck(Deck):
    def __init__(self, **kwargs) -> None:
        super().__init__(*CARDS[18:], **kwargs)