# standard libraries
from typing import List, Tuple

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube222 import moves_222
from rubikscubennnsolver.swaps import swaps_333

# fmt: off
moves_333 = moves_222
solved_333: str = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
centers_333: Tuple[int] = (
    5,  # Upper
    14,  # Left
    23,  # Front
    32,  # Right
    41,  # Back
    50,  # Down
)
edges_333: Tuple[int] = (
    2, 4, 6, 8,  # Upper
    11, 13, 15, 17,  # Left
    20, 22, 24, 26,  # Front
    29, 31, 33, 35,  # Right
    38, 40, 42, 44,  # Back
    47, 49, 51, 53,  # Down
)
corners_333: Tuple[int] = (
    1, 3, 7, 9,  # Upper
    10, 12, 16, 18,  # Left
    19, 21, 25, 27,  # Front
    28, 30, 34, 36,  # Right
    37, 39, 43, 45,  # Back
    46, 48, 52, 54,  # Down
)
# fmt: on


class RubiksCube333(RubiksCube):
    reduce333_orient_edges_tuples = (
        (2, 38),  # Upper
        (4, 11),
        (6, 29),
        (8, 20),
        (13, 42),  # Left
        (15, 22),
        (24, 31),  # Right
        (33, 40),
        (47, 26),  # Down
        (49, 17),
        (51, 35),
        (53, 44),
    )

    def solve(self, solution333: List[str] = None) -> None:
        """
        Solve the cube
        """

        if self.solved():
            return

        self.rotate_U_to_U()
        self.rotate_F_to_F()
        self.solve_333()
        self.compress_solution()


def rotate_333(cube: List[str], step: str) -> List[str]:
    """
    Args:
        cube: the cube to manipulate
        step: the move to apply to the cube

    Returns:
        the cube state after applying ``step``
    """
    return [cube[x] for x in swaps_333[step]]
