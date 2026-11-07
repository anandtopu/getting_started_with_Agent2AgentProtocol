def accept(card, keys):
    # YOUR CODE HERE: the presence of a signature is not proof.
    return bool(card.get("signatures"))
