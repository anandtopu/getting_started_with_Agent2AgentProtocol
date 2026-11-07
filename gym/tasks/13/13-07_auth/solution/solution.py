from agents.app import make_app


def build(tokens):
    return make_app("venues", tokens=tokens)
