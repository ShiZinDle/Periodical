from typing import Any, List, Union

from periodical.card import Card
from periodical.decks import Deck, StartingDeck


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self._deck = StartingDeck()
        self._discard = []
        self._hand = []
        self._table = []
        self._lab = []

    def __eq__(self, other: Any) -> bool:
        return (self.name == other.name
                and sorted(self._deck) == sorted(other._deck)
                and sorted(self._hand) == sorted(other._hand))

    def __str__(self) -> str:
        return self.name

    def _show(self, zone: List[Card]) -> str:
        return '\n'.join(map(str, sorted(zone)))

    def _get(self, zone: List[Card],
             numbers: bool = False) -> List[Union[Card, int]]:
        if numbers:
            return [card.number for card in zone]
        return zone

    def show_discard(self) -> str:
        return self._show(self._discard)

    def get_discard(self, numbers: bool = False) -> List[Card]:
        return self._get(self._discard, numbers)

    def show_hand(self) -> str:
        return self._show(self._hand)

    def get_hand(self, numbers: bool = False) -> List[Card]:
        return self._get(self._hand, numbers)

    def show_table(self) -> str:
        return self._show(self._table)

    def show_lab(self) -> str:
        return self._show(self._lab)

    def _draw(self) -> Card:
        if not self._deck:
            self._deck = Deck(*self._discard, *self._table)
            self._discard = []
            self._deck.shuffle()
        return self._deck.draw()

    def end_turn(self) -> None:
        for zone in (self._hand, self._table):
            self._discard.extend(zone)
        self._table = []
        self._hand = [self._draw() for _ in range(5)]

    def shuffle_deck(self) -> None:
        self._deck.shuffle()

    def _play(self, zone: List[Card], card: Card) -> None:
        zone.append(self._hand.pop(self._hand.index(card)))

    def play_card(self, card: Card) -> None:
        self._play(self._table, card)

    def synthesize(self, card: Card) -> None:
        self._play(self._lab, card)