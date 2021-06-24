import json
from typing import Any, Dict, List, Optional, Tuple

from pygame.surface import Surface

from periodical.card import border_and_fill, Card
from periodical.config import (BLACK_FONT, BUTTON, BUTTON_BORDER, CARD,
                               ELEMENTS_AMOUNT, FONT, NUM, PATH, Pos, Zone)


def create_cards(elements: List[Dict[str, Any]],
                 first: int, last: int) -> List[Card]:
    '''Return list of cards based on the passed elements and the given range.

    Args:
        elements: Complete details of each element.
        first: Number of first element to create a card for.
        last: Number of last element to create a card for.

    Returns:
        List of cards each depicting a unique element.
    '''
    return [Card(element['name'], element['symbol'], element['number'],
                 element['atomic_mass'], element['category'],
                 element['shells'], Zone.LIMBO)
            for element in elements
            if first <= element['number'] <= last]


def get_element_info(path: str) -> Any:
    '''Extract element info from json file.

    Args:
        path: Path to json file.

    Returns:
        Complete details of each element.
    '''
    with open(path, 'r', encoding='utf-8') as file_handler:
        file = file_handler.read()
    return json.loads(file)['elements']


def generate_cards(*, first: Optional[int] = None,
                   last: Optional[int] = None) -> List[Card]:
    '''Return list of Card objects based on range.

    Args:
        first: Number of first element to create a card for.
        last: Number of last element to create a card for.

    Returns:
        List of cards each depicting a unique element.
    '''
    if not first:
        first = 1
    if not last:
        last = ELEMENTS_AMOUNT
    cards = create_cards(get_element_info(PATH), first, last)
    return cards


def interact_with(deck: List[Card], card: Card, add: bool = False) -> None:
    '''Add or remove card from the deck.

    identity comparison is used to ensure removal of desired card and not one
    with equal values.

    Args:
        deck: List of cards to interact with.
        card: Object to add or remove.
        add: Whether to add or remove the card.
    '''
    if add:
        deck.append(card)
    else:
        for i, c in enumerate(deck):
            if c is card:
                deck.pop(i)


def move_zone(deck: List[Card], zone: Zone) -> None:
    '''Change `zone` attribute value for all cards in deck.

    Args:
        deck: List of cards to apply changes to.
        zone: New zone of cards.
    '''
    for card in deck:
        card.zone = zone


def calc_surface_heights(height: NUM) -> Tuple[NUM, NUM]:
    '''return y pos of top and bottom card rows for a game zone.

    Args:
        height: Board height to calculate row positions for.

    Returns:
        Position of top and bottom row in the game zone.
    '''
    return ((height / 2 - CARD.height) / 2,
            (height * 2 - CARD.height) / 3)


def show_button(screen: Surface, text: str, pos: Pos, name: str) -> None:
    '''Paste a button image onto the game screen.

    Args:
        screen: Surface object onto which to paste images.
        text: Button's text.
        pos: Button's position on the screen.
        name: Name of button for coloring purposes.
    '''
    button = border_and_fill(BUTTON, name, BUTTON_BORDER)
    title = FONT.render(text, *BLACK_FONT)
    button_pos = button.get_rect(center=pos.pos)
    title_pos = title.get_rect(center=button_pos.center)
    for surface, position in ((button, button_pos), (title, title_pos)):
        screen.blit(surface, position)
