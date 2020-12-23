# standard libraries
import logging
from typing import Any, List, Tuple

logger = logging.getLogger(__name__)


class SolveError(Exception):
    pass


def find_index_for_value(list_foo: List[Any], target: Any, min_index: int) -> int:
    """
    Args:
        list_foo: a list
        target: the item to look for
        min_index: the index must be at least this amount

    Returns:
        the index of ``target`` in ``list_foo``
    """
    for (index, value) in enumerate(list_foo):
        if value == target and index >= min_index:
            return index
    raise SolveError(f"Did not find {target} in list {sorted(list_foo)}")


def get_swap_count(listA: List[int], listB: List[int], debug) -> int:
    """
    Return the number of swaps we have to make in listB for it to match listA

    Args:
        listA: the first list
        listB: the second list
        debug: if True display debug output

    Returns:
        the number of swaps

    Example:

    .. code-block:: rst

        A = [1, 2, 3, 0, 4]
        B = [3, 4, 1, 0, 2]

    would require 2 swaps
    """
    A_length = len(listA)
    B_length = len(listB)
    swaps = 0
    index = 0

    if A_length != B_length:
        logger.info("listA %s" % " ".join(listA))
        logger.info("listB %s" % " ".join(listB))
        raise ValueError("listA (len %d) and listB (len %d) must be the same length" % (A_length, B_length))

    if debug:
        logger.info("INIT")
        logger.info("listA: %s" % " ".join(listA))
        logger.info("listB: %s" % " ".join(listB))
        logger.info("")

    while listA != listB:
        if listA[index] != listB[index]:
            listA_value = listA[index]
            listB_index_with_A_value = find_index_for_value(listB, listA_value, index + 1)
            tmp = listB[index]
            listB[index] = listB[listB_index_with_A_value]
            listB[listB_index_with_A_value] = tmp
            swaps += 1

            if debug:
                logger.info("index %d, swaps %d" % (index, swaps))
                logger.info("listA: %s" % " ".join(listA))
                logger.info("listB: %s" % " ".join(listB))
                logger.info("")
        index += 1

    if debug:
        logger.info("swaps: %d" % swaps)
        logger.info("")
    return swaps


def parse_ascii(state: str, size: int) -> str:
    """
    Args:
        state: an ascii picture of a cube
        size: the size of the cube

    Returns:
        a string of the cube state in ULFRBD order
    """
    U = []
    L = []
    F = []
    R = []
    B = []
    D = []

    lines = []
    for line in state.splitlines():
        line = line.strip().replace(" ", "")

        if line:
            lines.append(line)

    U = "".join(lines[0:size])

    for line in lines[size : size * 2]:
        L.append(line[0:size])
        F.append(line[size : size * 2])
        R.append(line[size * 2 : size * 3])
        B.append(line[size * 3 : size * 4])

    L = "".join(L)
    F = "".join(F)
    R = "".join(R)
    B = "".join(B)
    D = "".join(lines[size * 2 : size * 4])

    return "".join([U, L, F, R, B, D])


def parse_ascii_222(state: str) -> str:
    """
    Args:
        state: an ascii picture of a cube

    Returns:
        a string of the cube state in ULFRBD order
    """
    return parse_ascii(state, 2)


def parse_ascii_333(state: str) -> str:
    """
    Args:
        state: an ascii picture of a cube

    Returns:
        a string of the cube state in ULFRBD order
    """
    return parse_ascii(state, 3)


def parse_ascii_444(state: str) -> str:
    """
    Args:
        state: an ascii picture of a cube

    Returns:
        a string of the cube state in ULFRBD order
    """
    return parse_ascii(state, 4)


def parse_ascii_555(state: str) -> str:
    """
    Args:
        state: an ascii picture of a cube

    Returns:
        a string of the cube state in ULFRBD order
    """
    return parse_ascii(state, 5)


def parse_ascii_666(state: str) -> str:
    """
    Args:
        state: an ascii picture of a cube

    Returns:
        a string of the cube state in ULFRBD order
    """
    return parse_ascii(state, 6)


def parse_ascii_777(state: str) -> str:
    """
    Args:
        state: an ascii picture of a cube

    Returns:
        a string of the cube state in ULFRBD order
    """
    return parse_ascii(state, 7)


pre_steps_to_try: Tuple[Tuple[str]] = (
    (),
    ("U",),
    ("U'",),
    ("U2",),
    ("L",),
    ("L'",),
    ("L2",),
    ("F",),
    ("F'",),
    ("F2",),
    ("R",),
    ("R'",),
    ("R2",),
    ("B",),
    ("B'",),
    ("B2",),
    ("D",),
    ("D'",),
    ("D2",),
    ("U", "L"),
    ("U", "L'"),
    ("U", "L2"),
    ("U", "F"),
    ("U", "F'"),
    ("U", "F2"),
    ("U", "R"),
    ("U", "R'"),
    ("U", "R2"),
    ("U", "B"),
    ("U", "B'"),
    ("U", "B2"),
    ("U", "D"),
    ("U", "D'"),
    ("U", "D2"),
    ("U'", "L"),
    ("U'", "L'"),
    ("U'", "L2"),
    ("U'", "F"),
    ("U'", "F'"),
    ("U'", "F2"),
    ("U'", "R"),
    ("U'", "R'"),
    ("U'", "R2"),
    ("U'", "B"),
    ("U'", "B'"),
    ("U'", "B2"),
    ("U'", "D"),
    ("U'", "D'"),
    ("U'", "D2"),
    ("U2", "L"),
    ("U2", "L'"),
    ("U2", "L2"),
    ("U2", "F"),
    ("U2", "F'"),
    ("U2", "F2"),
    ("U2", "R"),
    ("U2", "R'"),
    ("U2", "R2"),
    ("U2", "B"),
    ("U2", "B'"),
    ("U2", "B2"),
    ("U2", "D"),
    ("U2", "D'"),
    ("U2", "D2"),
    ("L", "U"),
    ("L", "U'"),
    ("L", "U2"),
    ("L", "F"),
    ("L", "F'"),
    ("L", "F2"),
    ("L", "R"),
    ("L", "R'"),
    ("L", "R2"),
    ("L", "B"),
    ("L", "B'"),
    ("L", "B2"),
    ("L", "D"),
    ("L", "D'"),
    ("L", "D2"),
    ("L'", "U"),
    ("L'", "U'"),
    ("L'", "U2"),
    ("L'", "F"),
    ("L'", "F'"),
    ("L'", "F2"),
    ("L'", "R"),
    ("L'", "R'"),
    ("L'", "R2"),
    ("L'", "B"),
    ("L'", "B'"),
    ("L'", "B2"),
    ("L'", "D"),
    ("L'", "D'"),
    ("L'", "D2"),
    ("L2", "U"),
    ("L2", "U'"),
    ("L2", "U2"),
    ("L2", "F"),
    ("L2", "F'"),
    ("L2", "F2"),
    ("L2", "R"),
    ("L2", "R'"),
    ("L2", "R2"),
    ("L2", "B"),
    ("L2", "B'"),
    ("L2", "B2"),
    ("L2", "D"),
    ("L2", "D'"),
    ("L2", "D2"),
    ("F", "U"),
    ("F", "U'"),
    ("F", "U2"),
    ("F", "L"),
    ("F", "L'"),
    ("F", "L2"),
    ("F", "R"),
    ("F", "R'"),
    ("F", "R2"),
    ("F", "B"),
    ("F", "B'"),
    ("F", "B2"),
    ("F", "D"),
    ("F", "D'"),
    ("F", "D2"),
    ("F'", "U"),
    ("F'", "U'"),
    ("F'", "U2"),
    ("F'", "L"),
    ("F'", "L'"),
    ("F'", "L2"),
    ("F'", "R"),
    ("F'", "R'"),
    ("F'", "R2"),
    ("F'", "B"),
    ("F'", "B'"),
    ("F'", "B2"),
    ("F'", "D"),
    ("F'", "D'"),
    ("F'", "D2"),
    ("F2", "U"),
    ("F2", "U'"),
    ("F2", "U2"),
    ("F2", "L"),
    ("F2", "L'"),
    ("F2", "L2"),
    ("F2", "R"),
    ("F2", "R'"),
    ("F2", "R2"),
    ("F2", "B"),
    ("F2", "B'"),
    ("F2", "B2"),
    ("F2", "D"),
    ("F2", "D'"),
    ("F2", "D2"),
    ("R", "U"),
    ("R", "U'"),
    ("R", "U2"),
    ("R", "L"),
    ("R", "L'"),
    ("R", "L2"),
    ("R", "F"),
    ("R", "F'"),
    ("R", "F2"),
    ("R", "B"),
    ("R", "B'"),
    ("R", "B2"),
    ("R", "D"),
    ("R", "D'"),
    ("R", "D2"),
    ("R'", "U"),
    ("R'", "U'"),
    ("R'", "U2"),
    ("R'", "L"),
    ("R'", "L'"),
    ("R'", "L2"),
    ("R'", "F"),
    ("R'", "F'"),
    ("R'", "F2"),
    ("R'", "B"),
    ("R'", "B'"),
    ("R'", "B2"),
    ("R'", "D"),
    ("R'", "D'"),
    ("R'", "D2"),
    ("R2", "U"),
    ("R2", "U'"),
    ("R2", "U2"),
    ("R2", "L"),
    ("R2", "L'"),
    ("R2", "L2"),
    ("R2", "F"),
    ("R2", "F'"),
    ("R2", "F2"),
    ("R2", "B"),
    ("R2", "B'"),
    ("R2", "B2"),
    ("R2", "D"),
    ("R2", "D'"),
    ("R2", "D2"),
    ("B", "U"),
    ("B", "U'"),
    ("B", "U2"),
    ("B", "L"),
    ("B", "L'"),
    ("B", "L2"),
    ("B", "F"),
    ("B", "F'"),
    ("B", "F2"),
    ("B", "R"),
    ("B", "R'"),
    ("B", "R2"),
    ("B", "D"),
    ("B", "D'"),
    ("B", "D2"),
    ("B'", "U"),
    ("B'", "U'"),
    ("B'", "U2"),
    ("B'", "L"),
    ("B'", "L'"),
    ("B'", "L2"),
    ("B'", "F"),
    ("B'", "F'"),
    ("B'", "F2"),
    ("B'", "R"),
    ("B'", "R'"),
    ("B'", "R2"),
    ("B'", "D"),
    ("B'", "D'"),
    ("B'", "D2"),
    ("B2", "U"),
    ("B2", "U'"),
    ("B2", "U2"),
    ("B2", "L"),
    ("B2", "L'"),
    ("B2", "L2"),
    ("B2", "F"),
    ("B2", "F'"),
    ("B2", "F2"),
    ("B2", "R"),
    ("B2", "R'"),
    ("B2", "R2"),
    ("B2", "D"),
    ("B2", "D'"),
    ("B2", "D2"),
    ("D", "U"),
    ("D", "U'"),
    ("D", "U2"),
    ("D", "L"),
    ("D", "L'"),
    ("D", "L2"),
    ("D", "F"),
    ("D", "F'"),
    ("D", "F2"),
    ("D", "R"),
    ("D", "R'"),
    ("D", "R2"),
    ("D", "B"),
    ("D", "B'"),
    ("D", "B2"),
    ("D'", "U"),
    ("D'", "U'"),
    ("D'", "U2"),
    ("D'", "L"),
    ("D'", "L'"),
    ("D'", "L2"),
    ("D'", "F"),
    ("D'", "F'"),
    ("D'", "F2"),
    ("D'", "R"),
    ("D'", "R'"),
    ("D'", "R2"),
    ("D'", "B"),
    ("D'", "B'"),
    ("D'", "B2"),
    ("D2", "U"),
    ("D2", "U'"),
    ("D2", "U2"),
    ("D2", "L"),
    ("D2", "L'"),
    ("D2", "L2"),
    ("D2", "F"),
    ("D2", "F'"),
    ("D2", "F2"),
    ("D2", "R"),
    ("D2", "R'"),
    ("D2", "R2"),
    ("D2", "B"),
    ("D2", "B'"),
    ("D2", "B2"),
)
