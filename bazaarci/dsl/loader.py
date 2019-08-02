import os
import textx

from bazaarci.runner import Graph, Step, Product


METAMODEL = textx.metamodel_from_file(os.path.join(os.path.dirname(__file__), "bazaar.tx"))


def load(filename):
    model = METAMODEL.model_from_file(filename)
    return model
