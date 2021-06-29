from abc import ABC
from random import shuffle
from typing import Any, Optional

from periodical.card import Card
from periodical.config import ELEMENTS_AMOUNT, Zone
from periodical.utils import generate_cards, move_zone


class Deck(ABC):
    """A class for representing a deck of cards."""
    def __init__(self, zone: Zone, *cards: Card,  **kwargs: Any) -> None:
        super().__init__(**kwargs)  # type: ignore
        self._cards = list(cards)
        move_zone(self._cards, zone)

    def __bool__(self) -> bool:
        return len(self._cards) != 0

    def __len__(self) -> int:
        return len(self._cards)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Deck):
            return NotImplemented
        return sorted(self._cards) == sorted(other._cards)

    def draw(self) -> Optional[Card]:
        """Draws a card from the deck, if possible."""
        try:
            return self._cards.pop(0)
        except IndexError:
            return None

    def shuffle(self) -> None:
        """Randomizes the order of cards in the deck."""
        shuffle(self._cards)


class StartingDeck(Deck):
    """A class for representing a player's starting deck of cards."""
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(Zone.PLAYER_DECK, *generate_cards(last=10), **kwargs)


class MarketDeck(Deck):
    """A class for representing a communal market deck of cards."""
    def __init__(self, amount: int, zone: Zone, *,
                 first: int = 1, last: int = ELEMENTS_AMOUNT,
                 **kwargs: Any) -> None:
        cards = []
        for _ in range(amount):
            cards.extend(generate_cards(first=first, last=last))
        super().__init__(zone, *cards, **kwargs)
