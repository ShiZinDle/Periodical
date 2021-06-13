from pygame.font import Font
from card import border_and_fill, move_zone
from random import choice
from typing import Dict, List, Optional, Tuple, Union

import pygame
from pygame import Surface
from pygame.locals import *

from periodical.card import Card
from periodical.config import *
from periodical.decks import Deck, generate_cards, HeavyDeck, LightDeck
from periodical.player import Player


class Game:
    _LIGHT_DECK_LIMIT = 3
    _HEAVY_DECK_LIMIT = 5

    def __init__(self, *names: Tuple[str]) -> None:
        self.names = list(names)
        self._status = False

    def add_player(self, name: str) -> bool:
        if not self._status:
            self.names.append(name)
            return True
        return False

    def remove_player(self, name:str) -> bool:
        if not self._status:
            try:
                self.names.remove(name)
            except ValueError:
                return False
            else:
                return True
        return False

    def _set_players(self) -> None:
        self.players = [Player(name) for name in self.names]
        for player in self.players:
            player.shuffle_deck()
            player.end_turn()

    def _set_decks(self) -> None:
        self._light_deck = LightDeck()
        self._heavy_deck = HeavyDeck()
        for deck in (self._light_deck, self._heavy_deck):
            deck.shuffle()

    def _fill_market(self, market: List[Card], limit: int, zone: Zone,
                     deck: Deck) -> None:
        for _ in range(min(limit, len(deck)) - len(market)):
            card = deck.draw()
            card.zone = zone
            market.append(card)

    def _reset_general_market(self) -> None:
        self.general_market = generate_cards(last=2)
        move_zone(Zone.GENERAL_MARKET, self.general_market)

    def _fill_all_markets(self)  -> None:
        self._reset_general_market()
        for market, limit, zone, deck in (
            (self.light_market, self._LIGHT_DECK_LIMIT,
             Zone.LIGHT_MARKET, self._light_deck),
            (self.heavy_market, self._HEAVY_DECK_LIMIT,
             Zone.HEAVY_MARKET, self._heavy_deck)):
            self._fill_market(market, limit, zone, deck)

    def _set_board(self) -> None:
        self.light_market = []
        self.heavy_market = []
        self._fill_all_markets()

    def _interact_with(self, zone: List[Card], card: Card,
                       add: bool = False) -> None:
        if add:
            zone.append(card)
        else:
            zone.remove(card)

    def update_zones(self) -> None:
        self._zones_interaction = {
            Zone.HAND: lambda card, add:
                self.current_player.interact_with_hand(card, add),
            Zone.DISCARD: lambda card, add:
                self.current_player.interact_with_discard(card, add),
            Zone.TABLE: lambda card, add:
                self.current_player.interact_with_table(card, add),
            Zone.LAB: lambda card, add:
                self.current_player.interact_with_lab(card, add),
            Zone.LIGHT_MARKET: lambda card, add:
                self._interact_with(self.light_market, card, add),
            Zone.HEAVY_MARKET: lambda card, add:
                self._interact_with(self.heavy_market, card, add),
            Zone.GENERAL_MARKET: lambda card, add:
                self._interact_with(self.general_market, card, add),
            }

    def start(self) -> bool:
        if self.names and not self._status:
            self._set_players()
            self._set_decks()
            self._set_board()
            self.current_player = choice(self.players)
            self.update_zones()
            self._status = True
            self.show_board()
            return True
        return False

    def quit_game(self) -> bool:
        if self._status:
            self._status = False
            return True
        return False

    def end_turn(self) -> None:
        self.current_player.end_turn()
        self.current_player = self.players[
            self.players.index(self.current_player) - 1]
        self._fill_all_markets()

    def print_markets(self) -> str:
        message = ''
        for name, market in (('general market', self.general_market),
                           ('light market', self.light_market),
                           ('heavy market', self.heavy_market)):
            message += name + '\n\n'
            message += '\n'.join(map(str, sorted(market)))
            message += '-' * 20
        return message

    def _get_market(self, market: List[Card]) -> Dict[int, Card]:
        return {card.number: card for card in market}

    def buy_card(self, card: Card) -> bool:
        if self.current_player.buy_card(card):
            self._fill_all_markets()
            return True
        return False

    def show_market(self) -> Surface:
        cards = []
        location = left = 25

        top = sorted(self.general_market + self.light_market)
        bottom = sorted(self.heavy_market)
        top_height, bottom_height = Card.calc_surface_heights(MARKET)
        for zone, height in ((top, top_height), (bottom, bottom_height)):
            for card in zone:
                card.render()
                card.rect.update((MARKET.x + location,
                                MARKET.y + height), CARD.size)
                cards.append((card.img, card.rect))
                location += CARD.width + left
            location = left

        return cards

    def _get_all_cards(self) -> List[Card]:
        all_cards = []
        for deck in (self.general_market, self.light_market, self.heavy_market,
                     self.current_player.get_hand().values()):
            all_cards.extend(deck)
        return all_cards

    def _get_card_collision(self, pos: Tuple[int, int]) -> Optional[Card]:
        for card in self._get_all_cards():
            if card.rect.collidepoint(pos):
                return card

    def _check_button_collision(self, pos: Tuple[int, int]) -> None:
        if (self.current_player.can_mulligan() and
            Rect(MULLIGAN.pos, BUTTON.size).collidepoint(*pos)):
            self.current_player.mulligan()
        elif Rect(END_TURN.pos, BUTTON.size).collidepoint(*pos):
            self.end_turn()

    def _set_surface(self, screen: Surface, board: Board,
                     color: Tuple[int, int, int]) -> None:
        surface = Surface(board.size)
        surface.fill(color)
        screen.blit(surface, board.pos)

    def _validate_collide(self, board: Board, pos: Tuple[int, int]):
        return Rect(board.pos, board.size).collidepoint(*pos)

    def _validate_drag(self, pos: Tuple[int, int], card: Card) -> bool:
        if card.zone in (Zone.GENERAL_MARKET, Zone.LIGHT_MARKET,
                         Zone.HEAVY_MARKET):
            if any(map(lambda x: self._validate_collide(x, pos),
                       (HAND, TABLE))):
                if self.buy_card(card):
                    return True
        elif card.zone is Zone.HAND:
            # if self._validate_collide(TABLE, pos):  # irrelevant with no card effects
            #     self.current_player.play_card(card)
            #     return True
            if self._validate_collide(MARKET, pos):
                self.current_player.play_card(card, energy=True)
                return True
            if self._validate_collide(LAB, pos):
                if self.current_player.synthesize(card):
                    return True
        if card.zone in self._zones_interaction:
            self._zones_interaction[card.zone](card, add=True)
            return False


    def show_board(self) -> None:
        self.update_zones()
        pygame.init()
        screen = pygame.display.set_mode(SCREEN.size)
        pygame.display.set_caption('Periodical')

        card = None
        drag = False
        while True:
            for event in pygame.event.get():
                if (event.type == QUIT
                    or event.type == KEYDOWN
                    and event.key == K_ESCAPE):
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        card = self._get_card_collision(event.pos)
                        if card:
                            drag = True
                            mouse_x, mouse_y = event.pos
                            offset_x = card.rect.x - mouse_x
                            offset_y = card.rect.y - mouse_y
                            if card.zone in self._zones_interaction:
                                self._zones_interaction[card.zone](card,
                                                                   add=False)
                        self._check_button_collision(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        drag = False
                    if card:
                        self._validate_drag(pygame.mouse.get_pos(), card)

                elif event.type == pygame.MOUSEMOTION:
                    if drag:
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
                screen.blits(seq)

            self.current_player.show_buttons(screen)

            if card and pygame.mouse.get_pressed()[0]:
                screen.blit(card.img, (card.rect.x, card.rect.y))

            pygame.display.flip()