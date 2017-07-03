
from pprint import pformat
from rubikscubennnsolver import RubiksCube, ImplementThis
import logging

log = logging.getLogger(__name__)


class RubiksCubeNNNEven(RubiksCube):

    def __init__(self, kociemba_string, debug=False):
        RubiksCube.__init__(self, kociemba_string)

        if debug:
            log.setLevel(logging.DEBUG)

class RubiksCubeNNNOdd(RubiksCube):

    def __init__(self, kociemba_string, debug=False):
        RubiksCube.__init__(self, kociemba_string)

        if debug:
            log.setLevel(logging.DEBUG)
