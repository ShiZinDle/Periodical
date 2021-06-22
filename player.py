from typing import List, Optional

from pygame.surface import Surface

from periodical.card import Card
from periodical.config import (Board, CARD, CARD_IMG, DISCARD, END_TURN,
                               ENERGY, HAND, LAB, MULLIGAN, NUM, SYMBOL_HEIGHT,
                               TABLE, Zone)
from periodical.decks import Deck, StartingDeck
from periodical.utils import (calc_surface_heights, interact_with, move_zone,
                              show_button)


class Player:
    '''A class for representing a player in a card game.

    Attributs:
        name: Player's name.
    '''
    def __init__(self, name: str) -> None:
        self.name = name
        self._deck: Deck = StartingDeck()
        self._discard: List[Card] = []
        self._lab: List[Card] = []
        self._reset_zones()
        self._energy = 0
        self._played = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return NotImplemented
        return (self.name == other.name
                and self._deck == other._deck
                and sorted(self._hand) == sorted(other._hand))

    def __str__(self) -> str:
        return self.name

    def _get(self, zone: List[Card]) -> List[Card]:
        '''Return list of card in the passed zone.

        Args:
            zone: Game zone for which to retrun list of cards.

        Returns:
            List of card in the passed zone.
        '''
        return [card for card in zone]

    def get_hand(self) -> List[Card]:
        '''Return a list of cards in player's hand.

        Returns:
            List of cards in player's hand.
        '''
        return self._get(self._hand)

    def get_lab(self) -> List[Card]:
        '''Return a list of cards in player's lab.

        Returns:
            List of cards in player's lab.
        '''
        return self._get(self._lab)

    def get_table(self) -> List[Card]:
        '''Return a list of cards played or bought by the player during the
        current turn.

        Returns:
            List of cards played or bought by the player during the current
            turn.
        '''
        return self._get(self._table)

    def _draw(self) -> None:
        '''Add a card from the player's deck to their hand. Shuffle deck if
        necessary.
        '''
        if not self._deck:
            self._deck = Deck(Zone.PLAYER_DECK, *self._discard)
            self._discard = []
            self._deck.shuffle()
        card = self._deck.draw()
        if card:
            card.zone = Zone.HAND
            self._hand.append(card)

    def _reset_zones(self) -> None:
        '''Remove all cards from player's turn dependant zones.'''
        self._table: List[Card] = []
        self._hand: List[Card] = []
        self._unused: List[Card] = []
        self._last_synthesis: Optional[Card] = None

    def end_turn(self) -> None:
        '''End the player's turn.'''
        if self._hand:
            self._played = True
        for zone in (self._hand, self._table):
            move_zone(zone, Zone.DISCARD)
            self._discard.extend(zone)
        self._reset_zones()
        for _ in range(5):
            self._draw()
        self._last_synthesis = None
        self._energy = 0

    def shuffle_deck(self) -> None:
        '''Shuffle player's deck.'''
        self._deck.shuffle()

    def can_mulligan(self) -> bool:
        '''Return wether or not the player can perform a mulligan.

        A mulligan is the act of drawing a replacement initial hand (in this
        game: the remaining cards in the deck). Player's are eligible for
        a mulligan during their first turn and only if the have not performed
        any actions.

        Returns:
            True if the player can mulligan, False otherwise.'''
        return (len(self._deck) == 5
                and len(self._hand) == 5
                and not self._played)

    def mulligan(self) -> bool:
        '''Perform a mulligan.

        Returns:
            True if successful, False otherwise.'''
        if self.can_mulligan():
            self.end_turn()
            return True
        return False

    def _get_card_from_unused(self, card: Card) -> Card:
        '''Return card to remove from unused cards.

        If `card` is in the unused cards it will be returned. Otherwise, a card
        with equal values will be returned instead.

        Args:
            card: card due to be removed from unused cards.

        Returns:
            Actual card object to remove from unused cards.'''
        for other in self._unused:
            if card is other:
                return card
            if card == other:
                temp = other
        return temp

    def _play(self, board: List[Card], card: Card, zone: Zone) -> None:
        '''Play card to board and change its zone.

        Args;
            board: List of cards to add the played card to.
            card: Card to be played.
            zone: Zone to move card to.
        '''
        board.append(card)
        card.zone = zone

    # irrelevant with no card effects
    # def play_card(self, card: Card) -> None:
    #     '''Play card to the table and activate its effect.

    #     Args:
    #         card: Card to be played.
    #     '''
    #     self._play(self._table, card, Zone.TABLE)

    def harvest_card(self, card: Card, reverse: bool = False) -> bool:
        '''Play card for its energy value, or return previously harvested card
        to hand.

        Args:
            card: Card to be harvested.
            reverse: Wether or not to reverse the proccess.

        Returns:
            True if Successful, False otherwise.'''
        if reverse:
            if card in self._unused:
                card = self._get_card_from_unused(card)
                self.interact_with_unused(card)
                self._energy -= card.number
                self.interact_with_table(card)
                self._hand.append(card)
                card.zone = Zone.HAND
                return True
            return False

        self._play(self._table, card, Zone.TABLE)
        self._energy += card.number
        self._unused.append(card)
        return True

    def synthesize(self, card: Card, reverse: bool = False) -> bool:
        '''Add card to the lab.

        Only one synthesis is allowed each turn.

        Args:
            card: card to be synthesized.
            reverse: Wether or not to reverse the proccess.

        Returns:
            True if successful, False otherwise.
        '''
        if reverse:
            if card == self._last_synthesis:
                self._last_synthesis = None
                self._hand.append(card)
                card.zone = Zone.HAND
                return True
            return False

        if not self._last_synthesis and card:
            self._last_synthesis = card
            self._play(self._lab, card, Zone.LAB)
            return True
        return False

    def buy_card(self, card: Card) -> bool:
        '''Buy a card from the market using energy harvested from cards.

        Args:
            card: Card to buy.

        Returns:
            True if successful, False otherwise.
        '''
        if card.mass > self._energy:
            return False
        self._energy = 0
        self._unused = []
        self._table.append(card)
        card.zone = Zone.TABLE
        return True

    def _show_horizontal(self, zone: List[Card],
                         board: Board) -> CARD_IMG:
        '''Return list of card image and location tuples to be printed on the
        screen.

        Used for horizontal boards.

        Args:
            zone: Game zone to be printed.
            board: Board the cards will be printed on.

        Returns:
            List of card image and location tuples to be printed.'''
        cards = []
        left = 25
        location: NUM = left

        height, bottom_height = calc_surface_heights(board.height)

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

    def _show_vertical(self, zone: List[Card],
                       board: Board) -> CARD_IMG:
        '''Return list of card image and location tuples to be printed on the
        screen.

        Used for vertical boards.

        Args:
            zone: Game zone to be printed.
            board: Board the cards will be printed on.

        Returns:
            List of card image and location tuples to be printed.'''
        cards = []
        location = 12.5
        top = 15

        width = (board.width - CARD.width) / 2

        seq = sorted(zone)
        if zone is self._lab:
            seq = sorted(sorted(zone), key=lambda x: x.category)

        for card in seq:
            card.render()
            card.rect.update((board.x + width,
                              board.y + location), CARD.size)
            cards.append((card.img, card.rect))
            location += SYMBOL_HEIGHT + top

        return cards

    def show_hand(self) -> CARD_IMG:
        '''Return visualization of cards in player's hand for printing to the
        screen.

        Returns:
            Visualization of cards to be printed.'''
        return self._show_horizontal(self._hand, HAND)

    def show_table(self) -> CARD_IMG:
        '''Return visualization of cards played during the current turn for
        printing to the screen.

        Returns:
            Visualization of cards to be printed.'''
        return self._show_horizontal(self._table, TABLE)

    def show_discard(self) -> CARD_IMG:
        '''Return visualization of cards in player's discard for printing to
        the screen.

        Returns:
            Visualization of cards to be printed.'''
        return self._show_vertical(self._discard, DISCARD)

    def show_lab(self) -> CARD_IMG:
        '''Return visualization of cards in player's lab for printing to the
        screen.

        Returns:
            Visualization of cards to be printed.'''
        return self._show_vertical(self._lab, LAB)

    def show_buttons(self, screen: Surface) -> None:
        '''Display relevant button on the screen.

        Args:
            screen: Surface object onto which to paste images.'''
        show_button(screen, 'End Turn', END_TURN, 'end_turn')
        if self.can_mulligan():
            show_button(screen, 'Mulligan', MULLIGAN, 'mulligan')
        show_button(screen, f'Energy: {self._energy}',
                            ENERGY, 'energy')

    def interact_with_hand(self, card: Card, add: bool = False) -> None:
        '''Add or remove card from hand.
        Args:
            card: Card to be added or removed.
            add: Wether to add or remove card, defaults to removal.'''
        interact_with(self._hand, card, add)

    def interact_with_discard(self, card: Card, add: bool = False) -> None:
        '''Add or remove card from discard.
        Args:
            card: Card to be added or removed.
            add: Wether to add or remove card, defaults to removal.'''
        interact_with(self._discard, card, add)

    def interact_with_table(self, card: Card, add: bool = False) -> None:
        '''Add or remove card from table.
        Args:
            card: Card to be added or removed.
            add: Wether to add or remove card, defaults to removal.'''
        interact_with(self._table, card, add)

    def interact_with_lab(self, card: Card, add: bool = False) -> None:
        '''Add or remove card from lab.
        Args:
            card: Card to be added or removed.
            add: Wether to add or remove card, defaults to removal.'''
        interact_with(self._lab, card, add)

    def interact_with_unused(self, card: Card, add: bool = False) -> None:
        '''Add or remove card from unused.
        Args:
            card: Card to be added or removed.
            add: Wether to add or remove card, defaults to removal.'''
        interact_with(self._unused, card, add)
