from typing import Any, Dict, List

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
        self._energy = 0
        self._free_mulligan = True
        self._free_lab = True

    def __eq__(self, other: Any) -> bool:
        return (self.name == other.name
                and self._deck == other._deck
                and sorted(self._hand) == sorted(other._hand))

    def __str__(self) -> str:
        return self.name

    def _show(self, zone: List[Card]) -> str:
        return '\n'.join(map(str, sorted(zone)))

    def _get(self, zone: List[Card]) -> Dict[int, Card]:
        return {card.number: card for card in zone}

    def show_discard(self) -> str:
        return self._show(self._discard)

    def get_discard(self) -> List[Card]:
        return self._get(self._discard)

    def show_hand(self) -> str:
        return self._show(self._hand)

    def get_hand(self) -> List[Card]:
        return self._get(self._hand)

    def show_table(self) -> str:
        return self._show(self._table)

    def show_lab(self) -> str:
        return self._show(self._lab)

    def show_energy(self) -> int:
        return self._energy

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
        self._free_lab = True

    def shuffle_deck(self) -> None:
        self._deck.shuffle()

    def mulligan(self) -> bool:
        if self._free_mulligan and len(self._hand) == 5:
            self._free_mulligan = False
            self.end_turn()
            return True
        return False

    def _get_card(self, number: int) -> Card:
        for card in self._hand:
            if card.number == number:
                return card

    def _play(self, zone: List[Card], card: Card) -> None:
        zone.append(self._hand.pop(self._hand.index(card)))

    def play_card(self, *numbers: int) -> None:
        for number in numbers:
            card = self._get_card(number)
            self._play(self._table, card)
            self._energy += card.number

    def synthesize(self, number: int) -> bool:
        card = self._get_card(number)
        if self._free_lab and card:
            self._free_lab = False
            self._play(self._lab, card)
            return True
        return False

    def buy_card(self, card: Card) -> bool:
        if card.mass > self._energy:
            return False
        self._energy = 0
        self._discard.append(card)
        return True