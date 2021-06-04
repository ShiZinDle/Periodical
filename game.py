from card import Card
from decks import Deck, HeavyDeck, LightDeck
from random import choice
from typing import List, Tuple

from periodical.player import Player


class Game:
    def __init__(self, *names: Tuple[str]) -> None:
        self.names = list(names)
        self._status = False

    def add_player(self, name: str) -> bool:
        if not self.status:
            self.names.append(name)
            return True
        return False

    def remove_player(self, name:str) -> bool:
        if not self.status:
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

    def _fill_market(self, market: List[Card], limit: int,
                     deck: Deck) -> None:
        for _ in range(min(limit, len(deck))):
            market.append(deck.draw())

    def _set_board(self) -> None:
        self.light_market = []
        self.heavy_market = []
        self._fill_market(self.light_market, 2, self._light_deck)
        self._fill_market(self.heavy_market, 5, self._heavy_deck)

    def start(self) -> bool:
        if not self._status:
            self._set_players()
            self._set_decks()
            self._set_board()
            self.current_player = choice(self.players)
            self._status = True
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

    def show_board(self) -> str:
        message = ''
        for name, zone in (('light market', self.light_market),
                     ('heavy market', self.heavy_market)):
            message += name + '\n\n'
            message += '\n'.join(map(str, sorted(zone)))
            message += '-' * 20
        return message