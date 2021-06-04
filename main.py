from periodical.game import Game

# from starting_deck import StartingDeck

# deck = StartingDeck()
# deck.shuffle()
# print(deck.draw())
# print()a
# print(deck.draw())

if __name__ == '__main__':
    game = Game('bob' , 'ross', 'steve', 'jeff')
    game.start()

    def display_turn() -> None:
        print(game.current_player)
        print('-' * 20)
        print('hand')
        print(game.current_player.show_hand())
        print('-' * 20)
        print('table\n')
        print(game.current_player.show_table())
        print('-' * 20)
        print('lab\n')
        print(game.current_player.show_lab())
        print('-' * 20)
        print('discard\n')
        print(game.current_player.show_discard())
        print('-' * 20)
        print(game.show_board())

    for _ in range(1):
        display_turn()
        cur = game.current_player
        hand = cur.get_hand()
        cur.play_card(hand[0])
        cur.synthesize(max(hand))
        display_turn()
        game.end_turn()

    # for card in cards:
    #     print(card.number, card.symbol, card.category)

    # groups = [card.category for card in cards]
    # categories = {category: groups.count(category) for category in set(groups)}
    # print(categories)

    # 30, 48, 80, 112, 114