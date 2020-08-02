"""
https://en.wikipedia.org/wiki/Combinatorial_number_system
"""

# standard libraries
import logging
import math

log = logging.getLogger(__name__)


def choose(a, b):
    """
    >>> choose(23, 8)
    490314

    >>> choose(9, 6)
    84

    >>> choose(8, 5)
    56

    >>> choose(4, 4)
    1

    >>> choose(3, 4)
    0

    >>> choose(0, 1)
    0

    >>> choose(7, -1)
    0
    """
    # log.info("a %s, b %s" % (a, b))
    if b < 0:
        return 0
    elif b == a:
        return 1
    elif b > a:
        return 0

    return int(math.factorial(a) / (math.factorial(b) * math.factorial(a - b)))


def encode(perm):
    """
    >>> encode([11, 10, 9, 8, 3, 2, 1, 0])
    425

    >>> encode([7, 6, 5, 4, 3, 2, 1, 0])
    0
    """
    perm_len = len(perm)
    k = perm_len
    i = 0
    total = 0

    while i < perm_len:
        result = choose(perm[i], k)
        # log.info("choose(%d, %d) returned %d" % (perm[i], k, result))
        total += result
        k -= 1
        i += 1

    return total


def decode(n, k, start):
    """
    >>> decode(0, 8, 24)
    [7, 6, 5, 4, 3, 2, 1, 0]

    >>> decode(425, 8, 24)
    [11, 10, 9, 8, 3, 2, 1, 0]
    """
    result = []

    for c in reversed(range(start)):
        result_choose = choose(c, k)
        # log.info("choose(%d, %d) returned %d (n is %d)" % (c, k, result_choose, n))

        if result_choose <= n:
            n -= result_choose
            k -= 1
            result.append(c)
            # log.info("update: n %d, k %d, c %d, result %s" % (n, k, c, ' '.join(map(str, result))))

        # log.info("")
        # log.info("")
    return result


def state_to_list(state):
    """
    >>> state_to_list('xxLL')
    [3, 2]

    >>> state_to_list('LLxx')
    [1, 0]

    >>> state_to_list('LxLx')
    [2, 0]

    >>> state_to_list('xLxL')
    [3, 1]
    """
    result = []

    for (index, char) in enumerate(state):
        if char != "x":
            result.append(index)

    result = list(reversed(sorted(result)))
    return result


def state_to_rank(state):
    """
    >>> state_to_rank('xxLL')
    5

    >>> state_to_rank('LLxx')
    0

    >>> state_to_rank('LxLx')
    1

    >>> state_to_rank('xLxL')
    4
    """
    state_list = state_to_list(state)
    result = encode(state_list)
    return result


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)20s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    # standard libraries
    import doctest

    doctest.testmod()
