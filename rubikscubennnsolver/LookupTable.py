# standard libraries
import datetime as dt
import hashlib
import json
import logging
import os
import resource
import shutil
import subprocess
from pathlib import Path
from subprocess import call
from typing import Dict, List, TextIO, Tuple

# rubiks cube libraries
from rubikscubennnsolver.RubiksSide import SolveError

logger = logging.getLogger(__name__)


class NoSteps(Exception):
    pass


class NoIDASolution(Exception):
    pass


class NoPruneTableState(Exception):
    pass


def find_first_last(
    linecount: int, cache: Dict[int, str], b_state_to_find: str, state_width: int
) -> Tuple[List[Tuple[int, str]], int, int]:
    """
    Speed up a binary search by using a cache of what states we have seen where in the file. Use this
    cache to return a narrowed down first and last line numbers to search.

    Args:
        linecount: the number of lines in the file
        cache: a list of (offset, state) tuples in the file
        b_state_to_find: binary form of the state to find

    Returns:
        an updated cache list
        the first line number to search
        the last line number to search
    """
    first = 0
    last = linecount - 1
    # logger.info("find_first_last for %s with cache\n%s" % (b_state_to_find, pformat(cache)))
    offsets = sorted(cache.keys())

    for offset in offsets:
        line = cache[offset]
        b_state = line[:state_width]

        if b_state < b_state_to_find:
            del cache[offset]
            first = offset
            # logger.info("state %s < b_state_to_find %s, to_delete %d, first %s" % (state, b_state_to_find, to_delete, first))

        elif b_state == b_state_to_find:
            first = offset
            last = offset
            # logger.info("state %s == b_state_to_find %s, to_delete %d, first %s, last %s" % (state, b_state_to_find, first, last))
            break

        else:
            last = offset
            # logger.info("state %s > b_state_to_find %s, last %s" % (state, b_state_to_find, last))
            break

    # from pprint import pformat
    # logger.info("find_first_last for %s, first %s, last %s, cache\n%s" % (b_state_to_find, first, last, pformat(cache)))
    return (first, last)


def binary_search(fh: TextIO, width: int, state_width: int, linecount: int, state_to_find: str) -> str:
    """
    Args:
        fh: the file to search
        width: the width of a line in the file
        state_width: the width of the state portion of the line
        linecount: the number of lines in the file
        state_to_find: the state we are looking for

    Returns:
        the value for state_to_find
    """
    first = 0
    last = linecount - 1

    while first <= last:
        midpoint = int((first + last) / 2)
        fh.seek(midpoint * width)

        line = fh.read(width)
        (b_state, value) = line.rstrip().split(":")

        if state_to_find < b_state:
            last = midpoint - 1

        elif state_to_find == b_state:
            return value

        else:
            first = midpoint + 1

    return None


def binary_search_list(states: List[str], b_state_to_find: str) -> Tuple[bool, int]:
    """
    Args:
        states: a list of strings to search
        b_state_to_find: the state to look for

    Returns
        True if we found ``b_state_to_find``
        the line number for ``b_state_to_find``
    """
    first = 0
    linecount = len(states)
    last = linecount - 1

    while first <= last:
        midpoint = int((first + last) / 2)
        b_state = bytearray(states[midpoint], encoding="utf-8")

        if b_state_to_find < b_state:
            last = midpoint - 1

        # If this is the line we are looking for, then read the entire line
        elif b_state_to_find == b_state:
            return (True, midpoint)

        else:
            first = midpoint + 1

    return (False, first)


def binary_search_multiple(
    fh: TextIO, width: int, state_width: int, linecount: int, states_to_find: List[str]
) -> Dict[str, str]:
    """
    Args:
        states_to_find: a list of states to search for

    Returns:
        a dictionary where the state is the key and the value is a move sequence or move count
    """
    states_to_find = sorted(states_to_find)
    cache = {}
    results = {}
    fh.seek(0)
    line = fh.read(width)
    cache[0] = line
    b_state_first = line[:state_width]

    fh.seek((linecount - 1) * width)
    line = fh.read(width)
    cache[linecount - 1] = line
    b_state_last = line[:state_width]

    for state_to_find in states_to_find:
        b_state_to_find = bytearray(state_to_find, encoding="utf-8")

        # This provides a pretty massive improvement when you are looking for 100k+ states
        if b_state_to_find < b_state_first:
            continue
        elif b_state_to_find > b_state_last:
            break

        (first, last) = find_first_last(linecount, cache, b_state_to_find, state_width)

        # logger.info("state_to_find %s, first %s, last %s, cache\n%s" % (state_to_find, first, last, pformat(cache)))
        while first <= last:
            midpoint = int((first + last) / 2)

            if midpoint in cache:
                line = cache[midpoint]
            else:
                fh.seek(midpoint * width)

                line = fh.read(width)

                # We did a read...reads are expensive...cache the read
                cache[midpoint] = line

            b_state = line[:state_width]

            if b_state_to_find < b_state:
                last = midpoint - 1

            # If this is the line we are looking for, then read the entire line
            elif b_state_to_find == b_state:
                (_, value) = line.decode("utf-8").rstrip().split(":")

                if value.isdigit():
                    value = int(value)

                results[state_to_find] = value
                break

            else:
                first = midpoint + 1

    return results


def get_file_vitals(filename: str) -> Tuple[int, int, int]:
    """
    Args:
        filename: the file to examine

    Returns:
        the width of each line
        the width of the state
        the number of lines in the file
    """
    size = os.path.getsize(filename)

    # Find the state_width for the entries in our .txt file
    with open(filename, "r") as fh:
        first_line = next(fh)
        width = len(first_line)
        (state, steps) = first_line.split(":")
        state_width = len(state)
        linecount = int(size / width)
        return (width, state_width, linecount)


def steps_cancel_out(prev_step: str, step: str) -> bool:
    """
    >>> steps_cancel_out(None, "U")
    False

    >>> steps_cancel_out("U", "U'")
    True

    >>> steps_cancel_out("U'", "U")
    True

    >>> steps_cancel_out("U2", "U2")
    True

    >>> steps_cancel_out("U", "U")
    False

    Returns:
        True if the steps cancel each other out
    """
    if prev_step is None:
        return False

    # U2 followed by U2 is a no-op
    if step == prev_step and step.endswith("2"):
        return True

    # U' followed by U is a no-op
    if prev_step.endswith("'") and not step.endswith("'") and step == prev_step[0:-1]:
        return True

    # U followed by U' is a no-op
    if not prev_step.endswith("'") and step.endswith("'") and step[0:-1] == prev_step:
        return True

    return False


def steps_on_same_face_and_layer(prev_step: str, step: str) -> bool:
    """
    >>> steps_on_same_face_and_layer(None, "U")
    False

    >>> steps_on_same_face_and_layer("U", "U")
    True

    >>> steps_on_same_face_and_layer("U", "U'")
    True

    >>> steps_on_same_face_and_layer("U", "U2")
    True

    >>> steps_on_same_face_and_layer("U", "D")
    False

    >>> steps_on_same_face_and_layer("U", "D'")
    False

    >>> steps_on_same_face_and_layer("U", "D2")
    False

    >>> steps_on_same_face_and_layer("U", "Uw")
    False

    >>> steps_on_same_face_and_layer("F2", "Fw'")
    False

    >>> steps_on_same_face_and_layer("3Uw2", "3Uw")
    True

    >>> steps_on_same_face_and_layer("Uw2", "3Uw")
    False

    >>> steps_on_same_face_and_layer("2-3Lw", "2-3Lw'")
    True

    >>> steps_on_same_face_and_layer("2-3Lw", "2-3Lw2")
    True

    >>> steps_on_same_face_and_layer("2-3Lw", "2-3Rw")
    False

    >>> steps_on_same_face_and_layer("2-3Lw", "Lw")
    False

    >>> steps_on_same_face_and_layer("2-3Lw", "3Lw")
    False

    Returns:
        True if the steps are on the same face and layer
    """
    if prev_step is None:
        return False

    if prev_step[0] != step[0]:
        return False

    if prev_step[0].isdigit():
        if prev_step[1] != step[1]:
            return False

    # chop the trailing '
    if prev_step[-1] == "'":
        prev_step = prev_step[:-1]

    if step[-1] == "'":
        step = step[:-1]

    # chop the trailing 2
    if prev_step[-1] == "2":
        prev_step = prev_step[:-1]

    if step[-1] == "2":
        step = step[:-1]

    # Note the number of rows being turned and chop it
    if prev_step[0].isdigit():
        prev_step_rows_to_rotate = int(prev_step[0])
        prev_step = prev_step[1:]
    else:
        if "w" in prev_step:
            prev_step_rows_to_rotate = 2
        else:
            prev_step_rows_to_rotate = 1

    if step[0].isdigit():
        step_rows_to_rotate = int(step[0])
        step = step[1:]
    else:
        if "w" in step:
            step_rows_to_rotate = 2
        else:
            step_rows_to_rotate = 1

    if prev_step_rows_to_rotate == step_rows_to_rotate:
        if prev_step == step:
            return True

    return False


def pretty_time(delta: dt.timedelta) -> str:
    """
    Args:
        delta: a delta between two dt.datetime objects

    Returns:
        a pretty string of the time delta
    """
    delta = str(delta)

    if delta.startswith("0:00:00."):
        delta_us = int(delta.split(".")[1])
        delta_ms = int(delta_us / 1000)

        if delta_ms >= 500:
            return f"\033[91m{delta_ms}ms\033[0m"
        else:
            return f"{delta_ms}ms"

    elif delta.startswith("0:00:01."):
        delta_us = int(delta.split(".")[1])
        delta_ms = 1000 + int(delta_us / 1000)
        return f"\033[91m{delta_ms}ms\033[0m"

    else:
        return f"\033[91m{delta}\033[0m"


def md5signature(filename: str) -> str:
    """
    Args:
        filename: the file to examine

    Returns:
        the md5 signature of the file
    """
    hasher = hashlib.md5()
    with open(filename, "rb") as fh:
        buf = fh.read()
        hasher.update(buf)
    return str(hasher.hexdigest())


def download_file_if_needed(filename: str) -> None:
    """
    Args:
        filename: the file to download
    """

    if not os.path.exists(filename):
        filename_gz = filename + ".gz"
        filename_gz_no_dir = filename_gz.split("/")[-1]

        if not os.path.exists(filename_gz):
            url = f"https://rubiks-cube-lookup-tables.s3.amazonaws.com/{filename_gz_no_dir}"
            logger.info(f"Downloading table via 'wget {url}'")
            call(["wget", url])

            if not os.path.exists(filename_gz_no_dir):
                raise Exception(f"failed to download {filename_gz} via {url}")

            shutil.move(filename_gz_no_dir, filename_gz)

        logger.info(f"gunzip {filename_gz}")
        call(["gunzip", filename_gz])


class LookupTable(object):
    """
    A base class for all lookup table classes
    """

    def __init__(
        self,
        parent,
        filename: str,
        state_target: str,
        linecount: int = None,
        max_depth: int = None,
        legal_moves: List[str] = None,
        all_moves: List[str] = None,
        illegal_moves: List[str] = None,
        use_state_index: bool = False,
        build_state_index: bool = False,
    ):
        self.parent = parent
        self.sides_all = (
            self.parent.sideU,
            self.parent.sideL,
            self.parent.sideF,
            self.parent.sideR,
            self.parent.sideB,
            self.parent.sideD,
        )

        if filename:
            LOOKUP_TABLES = "lookup-tables/"
            Path(LOOKUP_TABLES).mkdir(parents=True, exist_ok=True)
            self.filename = LOOKUP_TABLES + filename
            self.filename_bin = self.filename.replace(".txt", ".bin")
            self.filename_state_index = self.filename.replace(".txt", ".state_index")
            self.filename_gz = filename + ".gz" if filename else None
        else:
            self.filename = None
            self.filename_bin = None
            self.filename_state_index = None
            self.filename_gz = None

        self.desc = filename.replace("lookup-table-", "").replace(".txt", "") if filename else ""
        self.filename_exists = False
        self.linecount = linecount
        self.max_depth = max_depth
        self.avoid_oll = None
        self.preloaded_cache_dict = False
        self.preloaded_cache_set = False
        self.preloaded_cache_string = False
        self.fh_txt_seek_calls = 0
        self.fh_txt_cache = {}
        self.cache = {}
        self.cache_set = set()
        self.cache_list = []
        self.use_isdigit = False
        self.only_colors = ()
        self.printed_disk_io_warning = False
        self.ida_graph = {}
        self.ida_graph_node = None
        self.state_index_cache = {}
        self.width = 0
        self.state_width = 0

        if all_moves is None:
            all_moves = []

        if legal_moves is None:
            legal_moves = []

        if illegal_moves is None:
            illegal_moves = []

        if all_moves and illegal_moves and legal_moves:
            raise Exception("all_moves, illegal_moves and legal_moves are all defined")

        if legal_moves:
            self.legal_moves = legal_moves
        else:
            self.legal_moves = []

            for step in all_moves:
                if step not in illegal_moves:
                    self.legal_moves.append(step)

        if isinstance(state_target, tuple):
            self.state_target = set(state_target)
        elif isinstance(state_target, list):
            self.state_target = set(state_target)
        elif isinstance(state_target, set):
            self.state_target = state_target
        else:
            self.state_target = set((state_target,))

        if self.filename:
            assert self.linecount, f"{self} linecount is {self.linecount}"

            if use_state_index:
                if not build_state_index:
                    download_file_if_needed(self.filename_bin)
                    download_file_if_needed(self.filename_state_index)
                self.state_width = len(list(self.state_target)[0])

            else:
                download_file_if_needed(self.filename)

            if "perfect-hash" not in self.filename and os.path.exists(self.filename):
                # Find the state_width for the entries in our .txt file
                with open(self.filename, "r") as fh:
                    first_line = next(fh)
                    self.width = len(first_line)
                    (state, steps) = first_line.strip().split(":")
                    self.state_width = len(state)

                    if steps.isdigit():
                        self.use_isdigit = True
                        # logger.info("%s: use_isdigit is True" % self)

        self.hex_format = "%" + "0%dx" % self.state_width
        self.filename_exists = True

        # 'rb' mode is about 3x faster than 'r' mode
        if self.filename and os.path.exists(self.filename):
            self.fh_txt = open(self.filename, mode="rb")
        else:
            self.fh_txt = None

        COST_LENGTH = 1
        STATE_INDEX_LENGTH = 4
        self.ROW_LENGTH = COST_LENGTH + ((STATE_INDEX_LENGTH + COST_LENGTH) * len(self.legal_moves))

    def __str__(self) -> str:
        if self.desc:
            return self.desc
        return self.__class__.__name__

    def binary_search_multiple(self, states_to_find: List[str]) -> Dict[str, str]:
        """
        Args:
            states_to_find: a list of states to search for

        Returns:
            a dictionary where the state is the key and the value is a move sequence or move count
        """
        return binary_search_multiple(self.fh_txt, self.width, self.state_width, self.linecount, states_to_find)

    def binary_search(self, state_to_find: str) -> str:
        """
        Args:
            state_to_find: the state to search for

        Returns:
            a move sequence or move count
        """
        state_to_find = bytes(state_to_find, encoding="utf-8")
        (first, last) = find_first_last(self.linecount, self.fh_txt_cache, state_to_find, self.state_width)

        while first <= last:
            midpoint = int((first + last) / 2)

            if midpoint in self.fh_txt_cache:
                line = self.fh_txt_cache[midpoint]
            else:
                self.fh_txt.seek(midpoint * self.width)
                self.fh_txt_seek_calls += 1
                line = self.fh_txt.read(self.width)

                # We did a read...reads are expensive...cache the read
                self.fh_txt_cache[midpoint] = line

            b_state = line[: self.state_width]

            if state_to_find < b_state:
                last = midpoint - 1

            # If this is the line we are looking for, then read the entire line
            elif state_to_find == b_state:
                return line.decode("utf-8").rstrip()

            else:
                first = midpoint + 1

        return None

    def binary_search_cache_string(self, state_to_find: str) -> str:
        """
        Args:
            state_to_find: the state to search for

        Returns:
            a move sequence or move count
        """
        first = 0
        last = self.linecount - 1

        state_to_find = bytes(state_to_find, encoding="utf-8")

        while first <= last:
            midpoint = int((first + last) / 2)

            # Only read the 'state' part of the line (for speed)
            state_start = midpoint * self.width
            state_end = state_start + self.state_width
            state = self.cache_string[state_start:state_end]

            if state_to_find < state:
                last = midpoint - 1

            # If this is the line we are looking for, then read the entire line
            elif state_to_find == state:
                line_end = state_start + self.width
                line = self.cache_string[state_start:line_end]
                return line.decode("utf-8").rstrip()

            else:
                first = midpoint + 1

        return None

    def preload_cache_dict(self) -> None:
        """
        Load a lookup table into a dictionary
        """
        # logger.info("%s: begin preload cache dict" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        if "dummy" in self.filename:
            self.cache = {}
        else:
            # Another option here would be to store a list of (state, step) tuples and
            # then binary search through it. That takes about 1/6 the amount of memory
            # but would be slower.  I have not measured how much slower.
            with open(self.filename, "r") as fh:

                # The bottleneck is the building of the dictionary, moreso than reading from disk.
                for line in fh:
                    (state, steps) = line.rstrip().split(":")

                    # Store this as a string, not a list.  It takes more than 2x the memory to store steps.split()
                    # For solving a 7x7x7 this is the difference in requiring 3G of RAM vs 7G!!.
                    self.cache[state] = steps

        self.preloaded_cache_dict = True
        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        logger.info(f"{self}: end preload cache dict ({memory_delta} bytes delta, {memory_post} bytes total)")

    def preload_cache_set(self) -> None:
        """
        Load a lookup table into a set
        """
        # logger.info("%s: begin preload cache set" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        states = []

        if "dummy" in self.filename:
            pass
        else:
            # Another option here would be to store a list of (state, step) tuples and
            # then binary search through it. That takes about 1/6 the amount of memory
            # but would be slower.  I have not measured how much slower.
            with open(self.filename, "r") as fh:

                # The bottleneck is the building of the dictionary, moreso that reading from disk.
                for line in fh:
                    state = line[: self.state_width]
                    states.append(state)

        self.cache_set = set(states)
        self.preloaded_cache_set = True
        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        logger.info(f"{self}: end preload cache set ({memory_delta} bytes delta, {memory_post} bytes total)")

    def preload_cache_string(self) -> None:
        """
        Load a lookup table into a string
        """
        # logger.info("%s: begin preload cache string" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.cache_string = None

        if "dummy" in self.filename:
            pass
        else:
            # FYI if you try this on a file 2G or larger it will barf with an OS error 22
            with open(self.filename, "rb") as fh:
                self.cache_string = fh.read()

        self.preloaded_cache_string = True
        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        logger.info(
            f"{self}: end preload cache string ({memory_delta} bytes delta, {memory_post} bytes total, {len(self.cache_string)} characters)"
        )

    def steps(self, state_to_find: str = None) -> List[str]:
        """
        Args:
            state_to_find: the state to search for

        Returns:
            a list of the steps found in the lookup table for ``state_to_find``
        """
        assert state_to_find

        # If we are at one of our state_targets we do not need to do anything
        if state_to_find in self.state_target:
            return None

        if self.preloaded_cache_dict:
            steps = self.cache.get(state_to_find)
            if steps:
                return steps.split()
            else:
                return None

        elif self.preloaded_cache_set:

            if state_to_find in self.cache_set:
                # Binary search the file to get the value
                line = self.binary_search(state_to_find)
                (state, steps) = line.strip().split(":")
                steps_list = steps.split()
                return steps_list

        elif self.preloaded_cache_string:
            line = self.binary_search_cache_string(state_to_find)

            if line:
                (state, steps) = line.strip().split(":")
                steps_list = steps.split()
                return steps_list

        # Binary search the file to get the value
        else:
            if not self.printed_disk_io_warning:
                logger.info(f"{self}: is binary searching the disk")
                self.printed_disk_io_warning = True

            line = self.binary_search(state_to_find)

            if line:
                (state, steps) = line.strip().split(":")
                steps_list = steps.split()
                return steps_list

        return None

    def steps_cost(self, state_to_find: str) -> int:
        """
        Args:
            state_to_find: the state to search for

        Returns:
            the number of steps to solve ``state_to_find``
        """
        steps = self.steps(state_to_find)

        if steps is None:
            return 0
        else:
            if self.use_isdigit:
                return int(steps[0])
            else:
                return len(steps)

    def solve_old_school(self) -> None:

        while True:
            state = self.state()

            if state in self.state_target:
                break

            steps = self.steps(state)

            if steps:
                for step in steps:
                    self.parent.rotate(step)
            else:
                raise NoSteps(f"{self}: state {state} does not have steps")

    def solve(self) -> None:

        if not self.filename_exists:
            raise SolveError(f"{self.filename} does not exist")

        if "TBD" in self.state_target:
            tbd = True
        else:
            tbd = False

        while True:
            self.ida_graph_node = None
            (state, cost_to_goal) = self.ida_heuristic()

            if tbd:
                logger.info(
                    f"{self}: solve() state {state} vs state_target {self.state_target}, cost_to_goal {cost_to_goal}"
                )

            if state in self.state_target:
                break

            steps = self.steps(state)

            if steps:
                for step in steps:
                    self.parent.rotate(step)
            else:
                raise NoSteps(f"{self}: state {state} does not have steps")

    def heuristic(self, pt_state: str) -> int:
        """
        Args:
            pt_state: the prune table state

        Returns:
            the cost to solve ``pt_state``
        """
        if pt_state in self.state_target:
            return 0
        else:
            result = self.steps_cost(pt_state)

            if result == 0:
                # This can happen when using HashCostOnly if a state-target and some other random state
                # hash to the same bucket.

                # Make sure we know it if we are missing a ton of them for 5x5x5-step500-pair-last-eight-edges.
                # Sometimes we get the edges in an unsolvable state.
                if str(self) == "5x5x5-step500-pair-last-eight-edges":
                    logger.info(f"{self}: pt_state {pt_state} cost is 0 but this is not a state_target")
                else:
                    logger.debug(f"{self}: pt_state {pt_state} cost is 0 but this is not a state_target")

                result = self.max_depth + 1

            return result

    def state(self):
        raise Exception(f"{self} must implement state()")

    def build_ida_graph(self) -> None:
        """
        Build a JSON file that contains all of the nodes in our graph and their transitions to other nodes
        """
        assert self.legal_moves, "no legal_moves defined"
        parent = self.parent
        legal_moves = self.legal_moves
        ida_graph = {}
        self.preload_cache_dict()

        states = sorted(self.cache.keys())

        logger.info(f"{self}: state_index begin")
        with open(self.filename_state_index, "w") as fh:
            for (index, state) in enumerate(states):
                fh.write("%s:%d\n" % (state, index))

        subprocess.call(["./utils/pad-lines.py", self.filename_state_index])
        logger.info(f"{self}: state_index end")

        logger.info(f"{self}: json begin")
        index = 0

        for (state, steps) in self.cache.items():
            len_steps = len(steps.split())

            if state in self.state_target:
                len_steps = 0

            parent.nuke_edges()
            parent.nuke_corners()
            parent.nuke_centers()
            self.populate_cube_from_state(state, parent.state, steps)

            ida_graph[state] = {"cost": len_steps, "edges": {}}

            baseline_state = parent.state[:]

            for step in legal_moves:
                parent.rotate(step)
                state_for_step = self.state()
                ida_graph[state]["edges"][step] = state_for_step
                parent.state = baseline_state[:]

            index += 1

            if index % 100000 == 0:
                logger.info(f"{index:,}")

                # avoid running out of memory
                if index % 1000000 == 0:
                    with open(self.filename.replace(".txt", ".json") + f"-{index}", "w") as fh:
                        json.dump(ida_graph, fh, indent=True)
                        fh.write("\n")
                        ida_graph = {}

        with open(self.filename.replace(".txt", ".json"), "w") as fh:
            json.dump(ida_graph, fh, indent=True)
            fh.write("\n")

        logger.info(f"{self}: json end")

    def load_ida_graph(self) -> None:
        """
        Load our IDA graph into memory
        """
        with open(self.filename_bin, "rb") as fh:
            logger.info(f"{self}: load IDA graph begin")
            self.ida_graph = fh.read()
            logger.info(f"{self}: load IDA graph end")

    def load_state_index_cache(self) -> None:
        """
        Load our state index cached into memory
        """
        self.state_index_cache = {}

        with open(self.filename_state_index, "r") as fh:
            for line in fh:
                (state, state_index) = line.rstrip().split(":")
                self.state_index_cache[state] = int(state_index)

    def state_index(self, state: str = None) -> int:
        """
        Returns:
            the index of the current state
        """
        if state is None:
            state = self.state()

        if state in self.state_index_cache:
            return self.state_index_cache[state]

        (width, state_width, linecount) = get_file_vitals(self.filename_state_index)

        with open(self.filename_state_index, "r") as fh:
            state_index = binary_search(fh, width, state_width, linecount, state)

            if state_index is None:
                self.parent.enable_print_cube = True
                desc = f"state {state} not found in {self.filename_state_index}"
                self.parent.print_cube(desc)
                raise Exception(f"{self}: {desc}")

            state_index = int(state_index)
            self.state_index_cache[state] = state_index
            return state_index

    def state_index_multiple(self, states_to_find: List[str]) -> Dict[str, str]:
        (width, state_width, linecount) = get_file_vitals(self.filename_state_index)
        with open(self.filename_state_index, "rb") as fh:
            results = binary_search_multiple(fh, width, state_width, linecount, states_to_find)
            for (state, state_index) in results.items():
                self.state_index_cache[state] = state_index
            return results

    def reverse_state_index(self, state_index: int) -> str:
        """
        Args:
            state_index: the index of the state to return

        Returns:
            the state for ``state_index``
        """
        with open(self.filename_state_index, "r") as fh:
            for line in fh:
                if line.rstrip().endswith(f":{state_index}"):
                    return line.split(":")[0]

    def state_index_cost(self, state_index: int) -> int:
        return self.ida_graph[state_index * self.ROW_LENGTH]

    def ida_heuristic(self) -> Tuple[str, int]:
        """
        Returns:
            the lookup table state
            the cost to goal
        """
        if self.ida_graph_node is None:
            self.ida_graph_node = self.state_index()

        state_index = self.ida_graph_node
        cost_to_goal = self.ida_graph[state_index * self.ROW_LENGTH]
        lt_state = self.reverse_state_index(state_index)

        return (lt_state, cost_to_goal)


class LookupTableIDA(LookupTable):
    """
    A base class for IDA* lookup tables
    """

    def __init__(
        self,
        parent,
        filename: str,
        state_target: str,
        moves_all: List[str],
        moves_illegal: List[str],
        linecount: int = None,
        max_depth: int = None,
        legal_moves: List = None,
        multiplier: float = None,
    ):
        LookupTable.__init__(self, parent, filename, state_target, linecount, max_depth)
        self.recolor_positions = []
        self.recolor_map = {}
        self.nuke_corners = False
        self.nuke_edges = False
        self.nuke_centers = False
        self.min_edge_paired_count = 0
        self.multiplier = multiplier

        assert self.multiplier is None or self.multiplier >= 1.0

        for x in moves_illegal:
            if x not in moves_all:
                raise ValueError(f"illegal move {x} is not in the list of legal moves")

        if legal_moves:
            self.moves_all = list(legal_moves)
        else:
            self.moves_all = []

            for x in moves_all:
                if x not in moves_illegal:
                    self.moves_all.append(x)

        # Cache the results of steps_on_same_face_and_layer() for all
        # combinations of moves we will see while searching.
        self.steps_on_same_face_and_layer_cache = {}
        self.steps_not_on_same_face_and_layer = {}

        for step1 in self.moves_all + [None]:
            for step2 in self.moves_all:
                if steps_on_same_face_and_layer(step1, step2):
                    self.steps_on_same_face_and_layer_cache[(step1, step2)] = True
                else:
                    self.steps_on_same_face_and_layer_cache[(step1, step2)] = False

                    if step1 not in self.steps_not_on_same_face_and_layer:
                        self.steps_not_on_same_face_and_layer[step1] = []
                    self.steps_not_on_same_face_and_layer[step1].append(step2)

    def recolor(self) -> None:
        """
        re-color the cube per use_nuke_edges, etd and recolor_positions
        """

        if self.nuke_corners or self.nuke_edges or self.nuke_centers or self.recolor_positions:
            logger.info(f"{self}: recolor")

            if self.nuke_corners:
                self.parent.nuke_corners()

            if self.nuke_edges:
                self.parent.nuke_edges()

            if self.nuke_centers:
                self.parent.nuke_centers()

            for x in self.recolor_positions:
                x_color = self.parent.state[x]
                x_new_color = self.recolor_map.get(x_color)

                if x_new_color:
                    self.parent.state[x] = x_new_color

    def ida_search(
        self, steps_to_here: List[str], threshold: int, prev_step: str, prev_state: str
    ) -> Tuple[int, bool, List[str]]:
        """
        https://algorithmsinsight.wordpress.com/graph-theory-2/ida-star-algorithm-in-general/

        Args:
            steps_to_here: a list of the steps to get here
            threshold: if f_cost is above this number, stop searching
            prev_step: the last step we took to get here
            prev_state: the state of the cube after prev_step was applied

        Returns:
            the f_cost which is the cost_to_here plus the estimated cost to the goal
            True if we found a solution
            a list of the steps to get here
        """
        self.ida_count += 1

        # calculate f_cost which is the cost to where we are plus the estimated cost to reach our goal
        cost_to_here = len(steps_to_here)
        self.parent.state = prev_state[:]
        (lt_state, cost_to_goal) = self.ida_heuristic()

        if self.multiplier:
            cost_to_goal = cost_to_goal * self.multiplier

        f_cost = cost_to_here + cost_to_goal

        # ================
        # Abort Searching?
        # ================
        if f_cost >= threshold:
            return (f_cost, False, [])

        # Are we done?
        if cost_to_goal == 0:
            return (f_cost, True, steps_to_here)

        # If we have already explored the exact same scenario down another branch
        # then we can stop looking down this branch
        explored_cost_to_here = self.explored.get(lt_state, 99)
        if explored_cost_to_here <= cost_to_here:
            return (f_cost, False, [])
        self.explored[lt_state] = cost_to_here

        for step in self.steps_not_on_same_face_and_layer[prev_step]:
            self.parent.state = self.rotate_xxx(prev_state, step)

            (f_cost_tmp, found_solution, solution_steps) = self.ida_search(
                steps_to_here + [step], threshold, step, self.parent.state[:]
            )

            if found_solution:
                return (f_cost_tmp, True, solution_steps)

        self.parent.state = prev_state[:]
        return (f_cost, False, [])

    def solve(self, min_ida_threshold: int = None, max_ida_threshold: int = 99) -> bool:
        """
        The goal is to find a sequence of moves that will put the cube in a state that is one of our state_targets

        Args:
            min_ida_threshold: the starting IDA threshold
            max_ida_threshold: the final IDA threshold

        Returns:
            True if we found a solution
        """
        if self.parent.size == 2:
            # rubiks cube libraries
            from rubikscubennnsolver.RubiksCube222 import rotate_222

            self.rotate_xxx = rotate_222

        elif self.parent.size == 4:
            # rubiks cube libraries
            from rubikscubennnsolver.RubiksCube444 import rotate_444

            self.rotate_xxx = rotate_444

        elif self.parent.size == 5:
            # rubiks cube libraries
            from rubikscubennnsolver.RubiksCube555 import rotate_555

            self.rotate_xxx = rotate_555

        elif self.parent.size == 6:
            # rubiks cube libraries
            from rubikscubennnsolver.RubiksCube666 import rotate_666

            self.rotate_xxx = rotate_666

        elif self.parent.size == 7:
            # rubiks cube libraries
            from rubikscubennnsolver.RubiksCube777 import rotate_777

            self.rotate_xxx = rotate_777

        else:
            raise NotImplementedError(f"Need rotate_{self.parent.size}{self.parent.size}{self.parent.size}")

        # If this is a lookup table that is staging a pair of colors (such as U and D)
        # then recolor the cubies accordingly.
        self.pre_recolor_state = self.parent.state[:]
        self.pre_recolor_solution = self.parent.solution[:]
        self.recolor()

        # save cube state
        self.original_state = self.parent.state[:]
        self.original_solution = self.parent.solution[:]

        # Avoiding OLL is done by changing the edge parity from odd to even.
        # The edge parity toggles from odd to even or even to odd with every
        # quarter wide turn. Sanity check that avoiding OLL is possible for
        # this table.
        if self.avoid_oll is not None:
            # logger.info("%s: verify we can avoid OLL via moves %s" % (self, " ".join(self.moves_all)))
            for step in self.moves_all:
                if "w" in step and not step.endswith("2"):
                    logger.info(f"{self}: has avoid_oll {self.avoid_oll}")
                    break
            else:
                raise Exception(
                    f"{self}: has avoid_oll {self.avoid_oll} but there are no quarter wide turns among moves_all {self.moves_all}"
                )

        # Get the intial cube state and cost_to_goal
        (state, cost_to_goal) = self.ida_heuristic()

        # The cube is already in the desired state, nothing to do
        if cost_to_goal == 0:
            logger.info(f"{self}: cube state {state} is in our lookup table")
            tmp_solution = self.parent.solution[:]
            self.parent.state = self.pre_recolor_state[:]
            self.parent.solution = self.pre_recolor_solution[:]

            for step in tmp_solution[len(self.original_solution) :]:
                self.parent.rotate(step)

            return True

        # If we are here (odds are very high we will be) it means that the current
        # cube state is not in the desired state.  We must now perform an IDA search
        # until we find a sequence of moves that takes us to the desired state.
        if min_ida_threshold is None:
            min_ida_threshold = cost_to_goal

        start_time0 = dt.datetime.now()
        logger.info(f"{self}: IDA threshold range {min_ida_threshold}->{max_ida_threshold}")
        total_ida_count = 0

        for threshold in range(min_ida_threshold, max_ida_threshold + 1):
            steps_to_here = []
            start_time1 = dt.datetime.now()
            self.ida_count = 0
            self.explored = {}

            (f_cost, found_solution, solution_steps) = self.ida_search(
                steps_to_here, threshold, None, self.original_state[:]
            )
            total_ida_count += self.ida_count

            end_time1 = dt.datetime.now()
            delta = end_time1 - start_time1
            nodes_per_sec = int(self.ida_count / delta.total_seconds())
            logger.info(
                f"{self}: IDA threshold {threshold}, explored {self.ida_count} nodes in {pretty_time(delta)}, {nodes_per_sec} nodes-per-sec"
            )

            if found_solution:
                self.parent.state = self.pre_recolor_state[:]
                self.parent.solution = self.pre_recolor_solution[:]

                for step in solution_steps:
                    self.parent.rotate(step)

                delta = end_time1 - start_time0
                nodes_per_sec = int(total_ida_count / delta.total_seconds())
                logger.info(f"{self}: IDA explored {total_ida_count} nodes in {delta}, {nodes_per_sec} nodes-per-sec")
                return True

        logger.info(f"{self}: could not find a solution via IDA with max threshold of {max_ida_threshold}")
        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]
        raise NoIDASolution(f"{self} FAILED with range {min_ida_threshold}->{max_ida_threshold + 1}")
