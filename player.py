from card import border_and_fill, move_zone
from typing import Any, Dict, List, Optional, Tuple

from pygame import Surface
from pygame.font import Font
from pygame.locals import *

from periodical.card import Card
from periodical.config import *
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
        self._free_lab = True
        self._played = False

    def __eq__(self, other: Any) -> bool:
        return (self.name == other.name
                and self._deck == other._deck
                and sorted(self._hand) == sorted(other._hand))

    def __str__(self) -> str:
        return self.name

    def _get(self, zone: List[Card]) -> Dict[int, Card]:
        return {card.number: card for card in zone}

    def get_discard(self) -> List[Card]:
        return self._get(self._discard)

    def get_hand(self) -> List[Card]:
        return self._get(self._hand)

    def get_energy(self) -> int:
        return self._energy

    def _draw(self) -> Optional[Card]:
        if not self._deck:
            self._deck = Deck(Zone.PLAYER_DECK, *self._discard)
            self._discard = []
            self._deck.shuffle()
        card = self._deck.draw()
        if card:
            card.zone = Zone.HAND
        return card

    def end_turn(self) -> None:
        if self._hand:
            self._played = True
        for zone in (self._hand, self._table):
            move_zone(Zone.DISCARD, zone)
            self._discard.extend(zone)
        self._table = []
        self._hand = [self._draw() for _ in range(5)]
        self._free_lab = True

    def shuffle_deck(self) -> None:
        self._deck.shuffle()

    def can_mulligan(self) -> bool:
        return (len(self._deck) == 5
                and len(self._hand) == 5
                and not self._played)

    def mulligan(self) -> bool:
        if self.can_mulligan():
            self.end_turn()
            return True
        return False

    def _play(self, deck: List[Card], card: Card, zone: Zone) -> None:
        deck.append(card)
        card.zone = zone

    def play_card(self, card: Card, energy: bool = False) -> None:
        self._play(self._table, card, Zone.TABLE)
        if energy:
            self._energy += card.number

    def synthesize(self, card: Card) -> bool:
        if self._free_lab and card:
            self._free_lab = False
            self._play(self._lab, card, Zone.LAB)
            return True
        return False

    def buy_card(self, card: Card) -> bool:
        if card.mass > self._energy:
            return False
        self._energy = 0
        self._table.append(card)
        card.zone = Zone.TABLE
        return True

    def _show_horizontal(self, zone: List[Card],
                         board: Board) -> List[Tuple[Surface, Rect]]:
        cards = []
        location = left = 25

        height, bottom_height = Card.calc_surface_heights(board)

        for i, card in enumerate(sorted(zone)):
            if i == 5:
                location = left
                height = bottom_height
            card.render()
            card.rect.update((board.x + location,
                            board.y + height), CARD.size)
            cards.append((card.img, card.rect))
            location += CARD.width + left

        return cards

    def _show_vertical(self, zone: List[Card], board: Board,
                       lab: bool = False) -> List[Tuple[Surface, Rect]]:
        cards = []
        location = 12.5
        top = 15

        width = (board.width - CARD.width) / 2

        seq = sorted(zone)
        if lab:
            seq = sorted(zone, key=lambda x: x.category)

        for card in seq:
            card.render() 
            card.rect.update((board.x + width,
                              board.y + location), CARD.size)
            cards.append((card.img, card.rect))
            location += SYMBOL_HEIGHT + top

        return cards

    def show_hand(self) -> Surface:
        return self._show_horizontal(self._hand, HAND)

    def show_table(self) -> Surface:
        return self._show_horizontal(self._table, TABLE)

    def show_discard(self) -> Surface:
        return self._show_vertical(self._discard, DISCARD)

    def show_lab(self) -> Surface:
        return self._show_vertical(self._lab, LAB, True)

    def _show_button(screen: Surface, text: str,
                    pos: Pos, category: str) -> None:
        button = border_and_fill(BUTTON_BORDER, BUTTON, category)
        font = Font(None, 36)
        title = font.render(text, 1, (10, 10, 10))
        button_pos = button.get_rect(center=pos.pos)
        title_pos = title.get_rect(center=button_pos.center)
        for surface, pos in ((button, button_pos), (title, title_pos)):
            screen.blit(surface, pos)

    def show_buttons(self, screen: Surface) -> None:
        Player._show_button(screen, 'End Turn', END_TURN, 'end_turn')
        if self.can_mulligan():
            Player._show_button(screen, 'Mulligan', MULLIGAN, 'mulligan')
        Player._show_button(screen, f'Energy: {self._energy}', ENERGY, 'energy')

    def _interact_with(self, zone: List[Card], card: Card,
                       add: bool = False) -> None:
        if add:
            zone.append(card)
        else:
            zone.remove(card)

    def interact_with_hand(self, card: Card, add: bool = False) -> None:
        self._interact_with(self._hand, card, add)

    def interact_with_discard(self, card: Card, add: bool = False) -> None:
        self._interact_with(self._discard, card, add)

    def interact_with_table(self, card: Card, add: bool = False) -> None:
        self._interact_with(self._table, card, add)

    def interact_with_lab(self, card: Card, add: bool = False) -> None:
        self._interact_with(self._lab, card, add)