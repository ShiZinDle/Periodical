from random import choice
from typing import Dict, List, Tuple, Union

from periodical.card import Card
from periodical.decks import CARDS, Deck, HeavyDeck, LightDeck
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

    def _fill_market(self, market: List[Card], limit: int,
                     deck: Deck) -> None:
        for _ in range(min(limit, len(deck)) - len(market)):
            market.append(deck.draw())

    def _fill_all_markets(self)  -> None:
        for market, limit, deck in (
            (self.light_market, self._LIGHT_DECK_LIMIT, self._light_deck),
            (self.heavy_market, self._HEAVY_DECK_LIMIT, self._heavy_deck)):
            self._fill_market(market, limit, deck)

    def _set_board(self) -> None:
        self.general_market = CARDS[:2]
        self.light_market = []
        self.heavy_market = []
        self._fill_all_markets()

    def start(self) -> bool:
        if self.names and not self._status:
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
        self._fill_all_markets()

    def show_board(self) -> str:
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

    def find_card(self, number: int,
                  remove: bool = False) -> Union[bool, Card]:
        for market in (self.general_market, self.light_market,
                       self.heavy_market):
            cards = self._get_market(market)
            if number in cards:
                card = cards[number]
                if remove:
                    market.remove(card)
                    return True
                return card
        return False

    def buy_card(self, number: int) -> bool:
        card = self.find_card(number)
        if not card:
            return False
        if self.current_player.buy_card(card):
            return self.find_card(number, remove=True)