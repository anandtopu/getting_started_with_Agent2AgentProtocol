from agents.app import make_app


def build(tokens):
    # YOUR CODE HERE: this accidentally exposes the demo.
    return make_app("venues", demo=True)
