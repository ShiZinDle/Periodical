from config import ENERGY
from random import choice
from typing import Callable, Dict, List, Optional, Tuple

import pygame
from pygame.constants import KEYDOWN, K_ESCAPE, QUIT
from pygame.rect import Rect
from pygame.surface import Surface

from periodical.card import Card
from periodical.config import (BUTTON, BUTTON_AREA, Board, CARD, CARD_IMG,
                               COLORS, DISCARD, END_TURN, GENERAL_END, HAND,
                               HEAVY_AMOUNT, HEAVY_DECK_LIMIT, LAB,
                               LIGHT_AMOUNT, LIGHT_DECK_LIMIT, LIGHT_END,
                               LIGHT_START, MARKET, MIN_PLAYER_AMOUNT, NUM,
                               SCREEN, SPACE, TABLE, Zone)
from periodical.decks import Deck, MarketDeck
from periodical.player import Player
from periodical.utils import (calc_surface_heights, generate_cards,
                              interact_with, move_zone)


class Game:
    """A class for representing and initiating a card game.

    Attributes:
        names: Names of participating players.
    """
    def __init__(self, *names: str) -> None:
        self.names = list(names)
        self._status = False

    def add_player(self, name: str) -> bool:
        """Adds a new player to names. Works only if the game hasn't started.

        Args:
            name: Name of player to add.

        Return:
            True if successfull, False otherwise.
        """
        if not self._status:
            self.names.append(name)
            return True
        return False

    def remove_player(self, name: str) -> bool:
        """Removes a player from names. Works only if the game hasn't started.

        Args:
            name: Name of player to remove.

        Return:
            True if successfull, False otherwise.
        """
        if not self._status:
            try:
                self.names.remove(name)
            except ValueError:
                return False
            else:
                return True
        return False

    def _set_players(self) -> None:
        """Creates a Player instance for each name in names."""
        self.players = [Player(name) for name in self.names]
        for player in self.players:
            player.shuffle_deck()
            player.end_turn()

    def _set_decks(self) -> None:
        """Initiates the communal market decks."""
        self._light_deck = MarketDeck(LIGHT_AMOUNT, Zone.LIGHT_DECK,
                                      first=LIGHT_START, last=LIGHT_END)
        self._heavy_deck = MarketDeck(HEAVY_AMOUNT, Zone.HEAVY_DECK,
                                      first=LIGHT_END + 1)
        for deck in (self._light_deck, self._heavy_deck):
            deck.shuffle()

    def _fill_market(self, market: List[Card], limit: int, zone: Zone,
                     deck: Deck) -> None:
        """Reveals new cards to the market from the given Deck.

        Args:
            market: Market to add cards to.
            limit: Maximal number of cards to reveal.
            zone: Zone to move cards to.
            deck: Deck to draw cards from.
        """
        for _ in range(limit - len(market)):
            card = deck.draw()
            if card:
                card.zone = zone
                market.append(card)

    def _reset_general_market(self) -> None:
        """Refills the general market."""
        self.general_market = generate_cards(last=GENERAL_END)
        move_zone(self.general_market, Zone.GENERAL_MARKET)

    def _fill_all_markets(self) -> None:
        """Refills each market accordingly."""
        self._reset_general_market()
        for market, limit, zone, deck in (
            (self.light_market, LIGHT_DECK_LIMIT,
             Zone.LIGHT_MARKET, self._light_deck),
            (self.heavy_market, HEAVY_DECK_LIMIT,
             Zone.HEAVY_MARKET, self._heavy_deck)):
            self._fill_market(market, limit, zone, deck)

    def _set_board(self) -> None:
        """Creates market attributes and fill all markets."""
        self.light_market: List[Card] = []
        self.heavy_market: List[Card] = []
        self._fill_all_markets()

    def update_zones(self) -> None:
        """Updates zone interaction functions based on current player."""
        self._zones_interaction: Dict[Zone, Callable[[Card, bool], None]] = {
            Zone.HAND: lambda card, add:
                self.current_player.interact_with_hand(card, add),
            Zone.DISCARD: lambda card, add:
                self.current_player.interact_with_discard(card, add),
            Zone.TABLE: lambda card, add:
                self.current_player.interact_with_table(card, add),
            Zone.LAB: lambda card, add:
                self.current_player.interact_with_lab(card, add),
            Zone.LIGHT_MARKET: lambda card, add:
                interact_with(self.light_market, card, add),
            Zone.HEAVY_MARKET: lambda card, add:
                interact_with(self.heavy_market, card, add),
            Zone.GENERAL_MARKET: lambda card, add:
                interact_with(self.general_market, card, add),
            }

    def start(self) -> bool:
        """Starts the game. Works only if the game hasn't started and
        there are enough players.

        Returns:
            True if successfull, False otherwise.
        """
        if len(self.names) <= MIN_PLAYER_AMOUNT and not self._status:
            self._set_players()
            self._set_decks()
            self._set_board()
            self.current_player = choice(self.players)
            self.update_zones()
            self._status = True
            self.show_board()
            return True
        return False

    def end_turn(self) -> None:
        """Ends the current player's turn."""
        self.current_player.end_turn()
        self.current_player = self.players[
            self.players.index(self.current_player) - 1]
        self._fill_all_markets()

    def buy_card(self, card: Card) -> bool:
        """Attempts to buy the passed card.

        Args:
            card: Card to buy.

        Returns:
            True if successfull, False otherwise.
        """
        if self.current_player.buy_card(card):
            self._fill_all_markets()
            return True
        return False

    def show_market(self) -> CARD_IMG:
        """Creates an image of the market to be displayed on the screen."""
        cards = []
        location: NUM = SPACE

        top = sorted(self.general_market + self.light_market)
        bottom = sorted(self.heavy_market)
        top_height, bottom_height = calc_surface_heights(MARKET.height)
        for zone, height in ((top, top_height), (bottom, bottom_height)):
            for card in zone:
                card.render()
                card.rect.update((MARKET.x + location,
                                  MARKET.y + height), CARD.size)
                cards.append((card.img, card.rect))
                location += CARD.width + SPACE
            location = SPACE

        return cards

    def _get_all_moveable_cards(self) -> List[Card]:
        """Returns a list of all cards the current player can interact with.

        Returns:
            A list of all cards the current player can interact with.
        """
        all_cards = []
        for deck in (self.general_market, self.light_market, self.heavy_market,
                     self.current_player.get_hand(),
                     self.current_player.get_lab(),
                     self.current_player.get_table()):
            all_cards.extend(deck)
        return all_cards

    def _get_card_collision(self, pos: Tuple[int, int]) -> Optional[Card]:
        """Checks for mouse collision with cards, and returns relevant card if
        collision occurres.

        Args:
            pos: Mouse position.

        Returns:
            Card with which mouse collided, if exists.
        """
        for card in self._get_all_moveable_cards():
            if card.rect.collidepoint(pos):
                return card
        return None

    def _check_button_collision(self, pos: Tuple[NUM, NUM]) -> None:
        """Checks for mouse collision with buttons, and performs action if
        necessary.

        Args:
            pos: Mouse position.
        """
        rect = Rect((0, 0), BUTTON.size)
        rect.center = ENERGY.pos  # type: ignore
        if self.current_player.can_mulligan() and rect.collidepoint(*pos):
            self.current_player.mulligan()
        else:
            rect.center = END_TURN.pos  # type: ignore
            if rect.collidepoint(*pos):
                self.end_turn()

    def _set_surface(self, screen: Surface, board: Board,
                     color: Tuple[int, int, int]) -> None:
        """Creates a color filled surface and pastes it on the screen.

        Args:
            screen: Surface object onto which to paste images.
            board: Board size and position on the screen.
            color: RGB color to fill board.
        """
        surface = Surface(board.size)
        surface.fill(color)
        screen.blit(surface, board.pos)

    def _validate_collide(self, board: Board, pos: Tuple[int, int]) -> bool:
        """Checks if mouse position is inside given board.

        Args:
            board: Board size and position on the screen.
            pos: Mouse position.

        Returns:
            True if collision occurres, False otherwise.
        """
        return bool(Rect(board.pos, board.size).collidepoint(*pos))

    def _validate_drag(self, pos: Tuple[int, int], card: Card) -> bool:
        """Checks for collision with valid game zones, based on original zone
        of card and current mouse positioned area, and acts accordingly.

        Args:
            pos: Mouse position.
            card: Card to be moved.

        Returns:
            True if drag was successful, False otherwise.
        """
        if card.zone in (Zone.GENERAL_MARKET, Zone.LIGHT_MARKET,
                         Zone.HEAVY_MARKET):
            if any(map(lambda x: self._validate_collide(x, pos),
                       (HAND, TABLE))):
                if self.buy_card(card):
                    return True
        elif card.zone is Zone.HAND:
            # irrelevant with no card effects
            # if self._validate_collide(TABLE, pos):
            #     self.current_player.play_card(card)
            #     return True
            if self._validate_collide(MARKET, pos):
                self.current_player.harvest_card(card)
                return True
            if self._validate_collide(LAB, pos):
                if self.current_player.synthesize(card):
                    return True
        elif card.zone is Zone.TABLE:
            if self._validate_collide(HAND, pos):
                if self.current_player.harvest_card(card, reverse=True):
                    return True
        elif card.zone is Zone.LAB:
            if self._validate_collide(HAND, pos):
                if self.current_player.synthesize(card, reverse=True):
                    return True
        # return card to its original location
        self._zones_interaction[card.zone](card, True)
        return False

    def show_board(self) -> None:
        """Creates a visualization of the game and display it."""
        self.update_zones()
        screen = pygame.display.set_mode(SCREEN.size)  # type: ignore
        pygame.display.set_caption('Periodical')

        card = None
        while True:
            for event in pygame.event.get():
                if (event.type == QUIT or event.type == KEYDOWN
                        and event.key == K_ESCAPE):
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        card = self._get_card_collision(event.pos)
                        if card:
                            mouse_x, mouse_y = event.pos
                            offset_x = card.rect.x - mouse_x
                            offset_y = card.rect.y - mouse_y
                            if card.zone in self._zones_interaction:
                                self._zones_interaction[card.zone](card, False)
                        self._check_button_collision(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if card:
                            self._validate_drag(pygame.mouse.get_pos(), card)

                elif event.type == pygame.MOUSEMOTION:
                    if card:
                        mouse_x, mouse_y = event.pos
                        card.rect.x = mouse_x + offset_x
                        card.rect.y = mouse_y + offset_y

            for board, color in [
                (DISCARD, COLORS['discard']),
                (MARKET, COLORS['market']),
                (TABLE, COLORS['table']),
                (HAND, COLORS['hand']),
                (LAB, COLORS['lab']),
                (BUTTON_AREA, COLORS['button_area']),
                    ]:
                self._set_surface(screen, board, color)

            discard = self.current_player.show_discard()
            hand = self.current_player.show_hand()
            lab = self.current_player.show_lab()
            market = self.show_market()
            table = self.current_player.show_table()

            for seq in (discard, hand, lab, market, table):
                screen.blits(seq)  # type: ignore

            self.current_player.show_buttons(screen)

            if card and pygame.mouse.get_pressed(num_buttons=3)[0]:
                screen.blit(card.img, (card.rect.x, card.rect.y))

            pygame.display.flip()
