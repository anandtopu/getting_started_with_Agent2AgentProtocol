from common.security import verify_card


def accept(card, keys):
    try:
        verify_card(card, keys)
        return True
    except ValueError:
        return False
