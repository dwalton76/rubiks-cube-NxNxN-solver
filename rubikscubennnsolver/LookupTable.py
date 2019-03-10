#!/usr/bin/env python3

import cProfile as profile
import datetime as dt
from rubikscubennnsolver.RubiksSide import SolveError
from pprint import pformat
from pyhashxx import hashxx
from subprocess import call
import gc
import hashlib
import logging
import os
import resource
import subprocess
import sys


log = logging.getLogger(__name__)


class ImplementThis(Exception):
    pass


class NoSteps(Exception):
    pass


class NoIDASolution(Exception):
    pass


class NoPruneTableState(Exception):
    pass


def get_wing_pair_count_555(strA, strB):
    wing_count = 0
    edge_count = 0

    if strA == "tOVrPPQQWTRRsSSqTvuUUOVXpWwxXoYYyzZZ" and strB == "OOorPPQQWTRRsSSqTtuUUVVvpWwxXXYYyzZZ":
        debug = True
    else:
        debug = False

    # 000 000 000 011 111 111 112 222 222 222 333 333
    # 012 345 678 901 234 567 890 123 456 789 012 345

    # OOO PPP SqQ RrU xss TTT Yuu VVV WWW Xxq yyr ZZZ (14)
    # OOO PPP QQQ RRR SSS TTT UUU VVV WWW XXX YYY ZZZ (4)
    # SOY opR zqT urU xsp wTO Zuv tVr VWX sxq yyQ PzW
    '''
    matching_midges = []

    for midge in (1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34):
        if strA[midge] == strB[midge]:
            matching_midges.append(strA[midge].lower())
    '''

    if debug:
        log.info(' '.join(strA[i:i+3] for i in range(0, len(strA), 3)))
        log.info(' '.join(strB[i:i+3] for i in range(0, len(strB), 3)))
        #log.info(matching_midges)

    matches = []

    for edge_index in range(12):
        wing_pre = edge_index * 3
        midge = wing_pre + 1
        wing_post = wing_pre + 2

        wing_pre_A = strA[wing_pre]
        wing_pre_B = strB[wing_pre]
        midge_A = strA[midge]
        midge_B = strB[midge]
        wing_post_A = strA[wing_post]
        wing_post_B = strB[wing_post]

        if wing_pre_A == wing_pre_B:
            wing_count += 1

            if debug:
                log.info("wing_pre_A %s matches" % wing_pre_A)

            if wing_pre_A.lower() in matches:
                if debug:
                    log.info("edge %s will pair\n" % wing_pre_A)
                edge_count += 1
            else:
                matches.append(wing_pre_A.lower())

        if wing_post_A == wing_post_B:
            wing_count += 1

            if debug:
                log.info("wing_post_A %s matches" % wing_post_A)

            if wing_post_A.lower() in matches:
                if debug:
                    log.info("edge %s will pair\n" % wing_post_A)
                edge_count += 1
            else:
                matches.append(wing_post_A.lower())

    if debug:
        log.info("wing_count: %d" % wing_count)
        log.info("matches: %s" % pformat(matches))
        log.info("edge_count: %d" % edge_count)

    return (wing_count, edge_count)


def get_characters_common_count(strA, strB, start_index):
    """
    This assumes strA and strB are the same length
    """
    for (charA, charB) in zip(strA[start_index:], strB[start_index:]):
        if charA == charB:
            result += 1

    return result


def steps_cancel_out(prev_step, step):
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


def steps_on_same_face_and_layer(prev_step, step):
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
        if 'w' in prev_step:
            prev_step_rows_to_rotate = 2
        else:
            prev_step_rows_to_rotate = 1

    if step[0].isdigit():
        step_rows_to_rotate = int(step[0])
        step = step[1:]
    else:
        if 'w' in step:
            step_rows_to_rotate = 2
        else:
            step_rows_to_rotate = 1

    if prev_step_rows_to_rotate == step_rows_to_rotate:
        if prev_step == step:
            return True

    return False


def pretty_time(delta):
    delta = str(delta)

    if delta.startswith('0:00:00.'):
        delta_us = int(delta.split('.')[1])
        delta_ms = int(delta_us/1000)

        if delta_ms >= 500:
            return "\033[91m%sms\033[0m" % delta_ms
        else:
            return "%sms" % delta_ms

    elif delta.startswith('0:00:01.'):
        delta_us = int(delta.split('.')[1])
        delta_ms = 1000 + int(delta_us/1000)
        return "\033[91m%sms\033[0m" % delta_ms

    else:
        return "\033[91m%s\033[0m" % delta


def find_first_last(linecount, cache, b_state_to_find):
    cache.sort()
    first = 0
    last = linecount - 1
    to_delete = 0
    #log.info("find_first_last for %s with cache\n%s" % (b_state_to_find, pformat(cache)))

    for (offset, state) in cache:

        if state < b_state_to_find:
            to_delete += 1
            first = offset
            #log.info("state %s < b_state_to_find %s, to_delete %d, first %s" % (state, b_state_to_find, to_delete, first))

        elif state == b_state_to_find:
            first = offset
            last = offset
            #log.info("state %s == b_state_to_find %s, to_delete %d, first %s, last %s" % (state, b_state_to_find, first, last))
            break

        else:
            last = offset
            #log.info("state %s > b_state_to_find %s, last %s" % (state, b_state_to_find, last))
            break

    to_delete -= 1

    if to_delete > 0:
        cache = cache[to_delete:]

    #log.info("find_first_last for %s, deleted %s, first %s, last %s, cache\n%s" % (b_state_to_find, to_delete, first, last, pformat(cache)))
    return (cache, first, last)


def md5signature(filename):
    hasher = hashlib.md5()
    with open(filename, 'rb') as fh:
        buf = fh.read()
        hasher.update(buf)
    return hasher.hexdigest()


def rm_file_if_mismatch(filename, filesize, md5target):
    filename_gz = filename + ".gz"

    # This only happens if a new copy of the lookup table has been checked in...we need to delete
    # the one we have and download the new one.
    if os.path.exists(filename):
        if filesize is not None:
            if os.path.getsize(filename) != filesize:
                log.info("%s: filesize %s does not equal target filesize %s" % (filename, os.path.getsize(filename), filesize))
                os.remove(filename)

                if os.path.exists(filename_gz):
                    os.remove(filename_gz)

        elif md5target is not None:
            if md5signature(filename) != md5target:
                log.info("%s: md5 signature %s is not %s" % (filename, md5signature(filename), md5target))
                os.remove(filename)

                if os.path.exists(filename_gz):
                    os.remove(filename_gz)


def download_file_if_needed(filename, cube_size):

    if not os.path.exists(filename):
        filename_gz = filename + ".gz"

        if not os.path.exists(filename_gz):
            url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/%s" % (cube_size, cube_size, cube_size, filename_gz)
            log.info("Downloading table via 'wget %s'" % url)
            call(['wget', url])

        log.info("gunzip %s" % filename_gz)
        call(['gunzip', filename_gz])


def binary_search_list(states, b_state_to_find):
    first = 0
    linecount = len(states)
    last = linecount - 1

    while first <= last:
        midpoint = int((first + last)/2)
        b_state = bytearray(states[midpoint], encoding='utf-8')

        if b_state_to_find < b_state:
            last = midpoint - 1

        # If this is the line we are looking for, then read the entire line
        elif b_state_to_find == b_state:
            return (True, midpoint)

        else:
            first = midpoint + 1

    return (False, first)


def wide_count_turns(steps):
    count = 0

    for step in steps:
        if 'w' in step:
            count += 1

    return count


class LookupTable(object):
    heuristic_stats = {}

    # This is for tweaking the valeus in heuristic_stats
    heuristic_stats_error = 0

    def __init__(self, parent, filename, state_target, linecount, max_depth=None, filesize=None, md5=None):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.filename = filename
        self.filename_gz = filename + '.gz'
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.filename_exists = False
        self.linecount = linecount
        self.max_depth = max_depth
        self.avoid_oll = None
        self.avoid_pll = False
        self.preloaded_cache_dict = False
        self.preloaded_cache_set = False
        self.preloaded_cache_string = False
        self.ida_all_the_way = False
        self.fh_txt_seek_calls = 0
        self.cache = {}
        self.cache_set = set()
        self.cache_list = []
        self.filesize = filesize
        self.md5 = md5
        self.collect_stats = False
        self.use_isdigit = False
        self.only_colors = ()
        self.printed_disk_io_warning = False

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        #assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"

        if 'dummy' in self.filename:
            self.width = 0
            self.state_width = 0
        else:
            assert self.linecount, "%s linecount is %s" % (self, self.linecount)
            rm_file_if_mismatch(self.filename, self.filesize, self.md5)
            download_file_if_needed(self.filename, self.parent.size)

            if 'perfect-hash' in self.filename:
                self.width = 0
                self.state_width = 0
            else:
                # Find the state_width for the entries in our .txt file
                with open(self.filename, 'r') as fh:
                    first_line = next(fh)
                    self.width = len(first_line)
                    (state, steps) = first_line.strip().split(':')
                    self.state_width = len(state)

                    if steps.isdigit():
                        self.use_isdigit = True
                        #log.info("%s: use_isdigit is True" % self)

        self.hex_format = '%' + "0%dx" % self.state_width
        self.filename_exists = True

        if isinstance(state_target, tuple):
            self.state_target = set(state_target)
        elif isinstance(state_target, list):
            self.state_target = set(state_target)
        elif isinstance(state_target, set):
            self.state_target = state_target
        else:
            self.state_target = set((state_target, ))

        # 'rb' mode is about 3x faster than 'r' mode
        if 'dummy' in self.filename:
            self.fh_txt = None
        else:
            self.fh_txt = open(self.filename, mode='rb')

    def __str__(self):
        return self.desc

    def binary_search_multiple(self, states_to_find):
        states_to_find.sort()
        cache = []
        results = {}
        linecount = self.linecount
        width = self.width
        state_width = self.state_width
        fh_txt = self.fh_txt
        #log.info("\n\n\n\n\n\n")
        #log.info("binary_search_multiple called for %s" % pformat(states_to_find))

        fh_txt.seek(0)
        b_state_first = fh_txt.read(state_width)

        fh_txt.seek((linecount - 1) * width)
        b_state_last = fh_txt.read(state_width)

        (_, starting_index) = binary_search_list(states_to_find, b_state_first)
        #log.info("start at index %d" % starting_index)

        for state_to_find in states_to_find[starting_index:]:
            b_state_to_find = bytearray(state_to_find, encoding='utf-8')

            # This provides a pretty massive improvement when you are looking for 100k+ states
            if b_state_to_find < b_state_first:
                # This part is basically a no-op now that we binary_search states_to_find
                # for b_state_first to find the starting_index
                continue
            elif b_state_to_find > b_state_last:
                break

            if cache:
                (cache, first, last) = find_first_last(linecount, cache, b_state_to_find)
            else:
                first = 0
                last = linecount - 1

            #log.info("state_to_find %s, first %s, last %s, cache\n%s" % (state_to_find, first, last, pformat(cache)))
            while first <= last:
                midpoint = int((first + last)/2)
                fh_txt.seek(midpoint * width)

                # Only read the 'state' part of the line (for speed)
                b_state = fh_txt.read(state_width)

                # We did a read...reads are expensive...cache the read
                cache.append((midpoint, b_state))

                if b_state_to_find < b_state:
                    last = midpoint - 1

                # If this is the line we are looking for, then read the entire line
                elif b_state_to_find == b_state:
                    fh_txt.seek(midpoint * width)
                    line = fh_txt.read(width)
                    (_, value) = line.decode('utf-8').rstrip().split(':')
                    results[state_to_find] = value
                    break

                else:
                    first = midpoint + 1
            else:
                #results[state_to_find] = None
                pass

        return results

    def binary_search(self, state_to_find):
        first = 0
        last = self.linecount - 1
        state_to_find = bytes(state_to_find, encoding='utf-8')

        while first <= last:
            midpoint = int((first + last)/2)
            self.fh_txt.seek(midpoint * self.width)
            self.fh_txt_seek_calls += 1

            # Only read the 'state' part of the line (for speed)
            b_state = self.fh_txt.read(self.state_width)

            if state_to_find < b_state:
                last = midpoint - 1

            # If this is the line we are looking for, then read the entire line
            elif state_to_find == b_state:
                self.fh_txt.seek(midpoint * self.width)
                line = self.fh_txt.read(self.width)
                return line.decode('utf-8').rstrip()

            else:
                first = midpoint + 1

        return None

    def binary_search_cache_string(self, state_to_find):
        first = 0
        last = self.linecount - 1

        state_to_find = bytes(state_to_find, encoding='utf-8')

        while first <= last:
            self.fh_txt_seek_calls += 1
            midpoint = int((first + last)/2)

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
                return line.decode('utf-8').rstrip()

            else:
                first = midpoint + 1

        return None

    def preload_cache_dict(self):
        #log.info("%s: begin preload cache dict" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        if isinstance(self, LookupTableCostOnly):
            raise Exception("%s is a CostOnly table, no need to call preload_cache_dict()" % self)

        if 'dummy' in self.filename:
            self.cache = {}
        else:
            # Another option here would be to store a list of (state, step) tuples and
            # then binary search through it. That takes about 1/6 the amount of memory
            # but would be slower.  I have not measured how much slower.
            with open(self.filename, 'r') as fh:

                # The bottleneck is the building of the dictionary, moreso that reading from disk.
                for line in fh:
                    (state, steps) = line.rstrip().split(':')
                    # Store this as a string, not a list.  It takes more than 2x the memory to store steps.split()
                    # For solving a 7x7x7 this is the difference in requiring 3G of RAM vs 7G!!.
                    self.cache[state] = steps

        self.preloaded_cache_dict = True
        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        log.info("{}: end preload cache dict ({:,} bytes delta, {:,} bytes total)".format(self, memory_delta, memory_post))

    def preload_cache_set(self):
        #log.info("%s: begin preload cache set" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        states = []

        if isinstance(self, LookupTableCostOnly):
            raise Exception("%s is a CostOnly table, no need to call preload_cache_set()" % self)

        if 'dummy' in self.filename:
            pass
        else:
            # Another option here would be to store a list of (state, step) tuples and
            # then binary search through it. That takes about 1/6 the amount of memory
            # but would be slower.  I have not measured how much slower.
            with open(self.filename, 'r') as fh:

                # The bottleneck is the building of the dictionary, moreso that reading from disk.
                for line in fh:
                    state = line[:self.state_width]
                    states.append(state)

        self.cache_set = set(states)
        self.preloaded_cache_set = True
        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        log.info("{}: end preload cache set ({:,} bytes delta, {:,} bytes total)".format(self, memory_delta, memory_post))

    def preload_cache_string(self):
        #log.info("%s: begin preload cache string" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.cache_string = None
        state_len = 0

        if isinstance(self, LookupTableCostOnly):
            raise Exception("%s is a CostOnly table, no need to call preload_cache_string()" % self)

        if 'dummy' in self.filename:
            pass
        else:
            # FYI if you try this on a file 2G or larger it will barf with an OS error 22
            with open(self.filename, 'rb') as fh:
                self.cache_string = fh.read()

        self.preloaded_cache_string = True
        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        #log.info("{}: {:,} characters in cache".format(self, len(self.cache_string)))
        log.info("{}: end preload cache string ({:,} bytes delta, {:,} bytes total, {:,} characters)".format(self, memory_delta, memory_post, len(self.cache_string)))

    def steps(self, state_to_find=None):
        """
        Return a list of the steps found in the lookup table for the current cube state
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
                #log.info("%s: %s is in cache_set, line %s" % (self, state_to_find, line))
                (state, steps) = line.strip().split(':')
                steps_list = steps.split()
                return steps_list

        elif self.preloaded_cache_string:
            line = self.binary_search_cache_string(state_to_find)

            if line:
                #log.info("%s: %s is in cache_string, line %s" % (self, state_to_find, line))
                (state, steps) = line.strip().split(':')
                steps_list = steps.split()
                return steps_list

        # Binary search the file to get the value
        else:
            if not self.printed_disk_io_warning:
                log.info("%s: is binary searching the disk" % self)
                self.printed_disk_io_warning = True

            line = self.binary_search(state_to_find)
            if line:
                (state, steps) = line.strip().split(':')
                steps_list = steps.split()
                return steps_list

        return None

    def steps_cost(self, state_to_find):
        steps = self.steps(state_to_find)

        if steps is None:
            #log.info("%s: steps_cost None for %s (stage_target)" % (self, state_to_find))
            return 0
        else:
            if self.use_isdigit:
                return int(steps[0])
            else:
                #log.info("%s: steps_cost %d for %s (%s)" % (self, len(steps), state_to_find, ' '.join(steps)))
                return len(steps)

    def solve(self):

        if not self.filename_exists:
            raise SolveError("%s does not exist" % self.filename)

        if 'TBD' in self.state_target:
            tbd = True
        else:
            tbd = False

        while True:
            (state, _) = self.ida_heuristic()

            if tbd:
                log.info("%s: solve() state %s vs state_target %s" % (self, state, pformat(self.state_target)))

            if state in self.state_target:
                break

            steps = self.steps(state)

            if steps:
                for step in steps:
                    self.parent.rotate(step)
            else:
                #self.parent.print_cube()
                raise NoSteps("%s: state %s does not have steps" % (self, state))

    def heuristic(self, pt_state):
        if pt_state in self.state_target:
            return 0
        else:
            result = self.steps_cost(pt_state)

            if result == 0:
                # This can happen when using HashCostOnly if a state-target and some other random state
                # hash to the same bucket.

                # Make sure we know it if we are missing a ton of them for 5x5x5-step500-pair-last-eight-edges.
                # Sometimes we get the edges in an unsolvable state.
                if str(self) == '5x5x5-step500-pair-last-eight-edges':
                    log.info("%s: pt_state %s cost is 0 but this is not a state_target" % (self, pt_state))
                else:
                    log.debug("%s: pt_state %s cost is 0 but this is not a state_target" % (self, pt_state))
                #self.parent.enable_print_cube = True
                #raise NoPruneTableState("%s: pt_state %s cost is 0 but this is not a state_target" % (self, pt_state))

                if not isinstance(self, LookupTableHashCostOnly):
                    result = self.max_depth + 1

            return result

    def find_edge_entries_with_loose_signature(self, signature_to_find):
        """
        Given a signature such as 001001010110, return a list of all of the lines
        in our lookup-table that will not break up any of the paired edges (a 1
        represents a paired edge).

        This is only used by the 4x4x4 and 5x5x5 edges tables
        """
        result = []
        signature_to_find = int(signature_to_find, 2)

        with open(self.filename, 'r') as fh:
            for line in fh:

                # If signature_to_find is 0 we will add every line so no
                # need to bitwise AND the signatures
                if signature_to_find == 0:
                    result.append(line.rstrip())
                else:
                    signature = line.split('_')[0]
                    signature = int(signature, 2)

                    if (signature & signature_to_find) == signature_to_find:
                        result.append(line.rstrip())

        return result

    def find_edge_entries_with_signature(self, signature_to_find):
        """
        Given a signature such as 001001010110, return a list of all of the lines
        in our lookup-table that start with that signature.

        This is only used by 4x4x4 edges tables
        """
        self.fh_txt.seek(0)
        result = []

        first = 0
        last = self.linecount - 1
        signature_width = len(signature_to_find)
        b_signature_to_find = bytearray(signature_to_find, encoding='utf-8')

        fh = self.fh_txt

        # Find an entry with signature_to_find
        while first <= last:
            midpoint = int((first + last)/2)
            fh.seek(midpoint * self.width)

            # Only read the 'state' part of the line (for speed)
            b_signature = fh.read(signature_width)

            if b_signature_to_find < b_signature:
                last = midpoint - 1

            # If this is the line we are looking for
            elif b_signature_to_find == b_signature:
                break

            else:
                first = midpoint + 1
        else:
            log.warning("could not find signature %s" % signature_to_find)
            return result

        line_number_midpoint_signature_to_find = midpoint

        # Go back one line at a time until we are at the first line with signature_to_find
        while True:
            fh.seek(midpoint * self.width)

            line = fh.read(self.width)
            line = line.decode('utf-8').rstrip()
            (edges_state, steps) = line.split(':')
            (signature, _) = edges_state.split('_')

            if signature != signature_to_find:
                break

            result.append(line)
            midpoint -= 1

            if midpoint < 0:
                break


        # Go forward one line at a time until we have read all the lines
        # with signature_to_find
        midpoint = line_number_midpoint_signature_to_find + 1

        while midpoint <= self.linecount - 1:
            fh.seek(midpoint * self.width)
            line = fh.read(self.width)
            line = line.decode('utf-8').rstrip()
            (edges_state, steps) = line.split(':')
            (signature, _) = edges_state.split('_')

            if signature == signature_to_find:
                result.append(line)
            else:
                break

            midpoint += 1

        return result

    def state(self):
        raise Exception("child class must implement state()")

    def best_match(self, state_to_find, init_wing_count):
        max_wing_pair_count = 0
        max_line = None
        max_steps_len = 9999
        max_edges_pair_count = 0

        log.info("%s: %s is init state, %d wings paired" % (self, state_to_find, init_wing_count))
        with open(self.filename, "r") as fh:
            for line in fh:
                line = line.rstrip()
                (state, steps) = line.split(":")
                steps = steps.split()
                len_steps = len(steps)
                (wing_pair_count, edges_pair_count) = get_wing_pair_count_555(state_to_find, state)
                wing_pair_count -= init_wing_count

                # dwalton
                if (wing_pair_count > max_wing_pair_count or
                        (wing_pair_count == max_wing_pair_count and len_steps < max_steps_len) or
                        (wing_pair_count == max_wing_pair_count and len_steps == max_steps_len and edges_pair_count > max_edges_pair_count)):
                #if (edges_pair_count > max_edges_pair_count or
                #        (edges_pair_count == max_edges_pair_count and wing_pair_count > max_wing_pair_count) or
                #        (edges_pair_count == max_edges_pair_count and wing_pair_count > max_wing_pair_count and len_steps < max_steps_len)):

                    max_wing_pair_count = wing_pair_count
                    max_line = line.strip()
                    max_steps_len = len_steps
                    max_edges_pair_count = edges_pair_count
                    #log.info("%s: %s vs %s will pair %d wings in %d moves" % (self, state_to_find, state, max_wing_pair_count, max_steps_len))
                    log.info("%s: %s will pair %d wings and %d edges in %d moves %s" %
                        (self, state, max_wing_pair_count, max_edges_pair_count, max_steps_len, " ".join(steps)))

        return max_line


class LookupTableCostOnly(LookupTable):

    def __init__(self, parent, filename, state_target, linecount, max_depth=None, filesize=None, md5=None):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.filename = filename
        self.filename_gz = filename + '.gz'
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.filename_exists = False
        self.linecount = linecount
        self.max_depth = max_depth
        self.avoid_oll = None
        self.avoid_pll = False
        self.preloaded_cache_dict = False
        self.preloaded_cache_set = False
        self.ida_all_the_way = False
        self.filesize = filesize
        self.md5 = md5

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        #assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"

        if 'dummy' not in self.filename:
            assert self.linecount, "%s linecount is %s" % (self, self.linecount)

        rm_file_if_mismatch(self.filename, self.filesize, self.md5)
        download_file_if_needed(self.filename, self.parent.size)
        self.filename_exists = True

        if isinstance(state_target, tuple):

            if isinstance(state_target[0], int):
                self.state_width = 0
            else:
                self.state_width = len(state_target[0])

            self.state_target = set(state_target)

        elif isinstance(state_target, list):
            self.state_width = len(state_target[0])
            self.state_target = set(state_target)

        elif isinstance(state_target, int):
            self.state_width = 0
            self.state_target = set((state_target, ))

        else:
            self.state_width = len(state_target)
            self.state_target = set((state_target, ))

        self.hex_format = '%' + "0%dx" % self.state_width

        self.fh_txt_seek_calls = 0
        self.fh_txt = None

        # Some cost-only tables are 2^32 characters, we do not want to read a 4G
        # string into memory so for those we will seek()/read() through the file.
        # We do not have to binary_search() though so that cuts way down on the
        # number of reads.
        #log.info("%s: begin preload cost-only" % self)
        memory_pre = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        # There is a CPU/memory tradeoff to be made here with 'r' vs 'rb'. 'rb' takes
        # 1/2 the memory of 'r' but requires steps_cost() to call chr() everytime. This
        # is not super expensive though and a lot of the tables we load here are 165 million
        # entries so we are talking about using 165M vs 330M for each of those. We are
        # memory bound on raspberry Pi3 so use 'rb' and take the minor CPU hit.
        with open(self.filename, 'rb') as fh:
            self.content = fh.read()
        self.fh_txt_seek_calls += 1

        memory_post = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory_post - memory_pre
        log.info("{}: end preload cost-only ({:,} bytes delta, {:,} bytes total)".format(self, memory_delta, memory_post))

    def steps_cost(self, state_to_find):
        # state_to_find is an integer, there is a one byte hex character in the file for each possible state.
        # This hex character is the number of steps required to solve the corresponding state.
        return int(chr(self.content[state_to_find]), 16)


class LookupTableHashCostOnly(LookupTableCostOnly):

    def __init__(self, parent, filename, state_target, linecount, max_depth=None, bucketcount=None, filesize=None, md5=None):
        LookupTableCostOnly.__init__(self, parent, filename, state_target, linecount, max_depth, filesize, md5)
        self.bucketcount = bucketcount

    def steps_cost(self, state_to_find):

        # compute the hash_index for state_to_find, look that many bytes into the
        # file/self.content and retrieve a single hex character. This hex character
        # is the number of steps required to solve the corresponding state.
        hash_raw = hashxx(state_to_find.encode('utf-8'))
        hash_index = int(hash_raw % self.bucketcount)

        result = int(chr(self.content[hash_index]), 16)

        # This will be very rare but if a state_target and some other random state both hash
        # to the same bucket the cost will be 0.
        if not result:
            log.debug("%s: state_to_find %s, hash_raw %s. hash_index %s, result is %s" % (self, state_to_find, hash_raw, hash_index, result))
            #raise SolveError("%s: state_to_find %s, hash_raw %s. hash_index %s, result is %s" % (self, state_to_find, hash_raw, hash_index, result))

        return result


class LookupTableIDA(LookupTable):

    def __init__(self, parent, filename, state_target, moves_all, moves_illegal,
            linecount, max_depth=None, filesize=None, legal_moves=[]):
        LookupTable.__init__(self, parent, filename, state_target, linecount, max_depth, filesize)
        self.ida_nodes = {}
        self.recolor_positions = []
        self.recolor_map = {}
        self.nuke_corners = False
        self.nuke_edges = False
        self.nuke_centers = False
        self.min_edge_paired_count = 0

        for x in moves_illegal:
            if x not in moves_all:
                raise Exception("illegal move %s is not in the list of legal moves" % x)

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

    def search_complete(self, state, steps_to_here):

        if self.ida_all_the_way:
            if state not in self.state_target:
                return False
            steps = []

        else:
            if state in self.state_target:
                steps = []
            else:
                steps = self.steps(state)

                if not steps:
                    return False

        # =============================================
        # If there are steps for a state that means our
        # search is done...woohoo!!
        # =============================================
        # rotate_xxx() is very fast but it does not append the
        # steps to the solution so put the cube back in original state
        # and execute the steps via a normal rotate() call
        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        for step in steps_to_here:
            self.parent.state = self.rotate_xxx(self.parent.state[:], step)
            self.parent.solution.append(step)

        # The cube is now in a state where it is in the lookup table, we may need
        # to do several lookups to get to our target state though. Use
        # LookupTabele's solve() to take us the rest of the way to the target state.
        LookupTable.solve(self)

        if self.avoid_oll is not None:
            orbits_with_oll = self.parent.center_solution_leads_to_oll_parity()

            if self.avoid_oll in orbits_with_oll:
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
                log.debug("%s: IDA found match but it leads to OLL" % self)
                return False

        if self.avoid_pll and self.parent.edge_solution_leads_to_pll_parity():
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]
            log.debug("%s: IDA found match but it leads to PLL" % self)
            return False

        return True

    def ida_search(self, steps_to_here, threshold, prev_step, prev_state):
        """
        https://algorithmsinsight.wordpress.com/graph-theory-2/ida-star-algorithm-in-general/
        """
        self.ida_count += 1

        # calculate f_cost which is the cost to where we are plus the estimated cost to reach our goal
        cost_to_here = len(steps_to_here)
        self.parent.state = prev_state[:]
        (lt_state, cost_to_goal) = self.ida_heuristic()
        f_cost = cost_to_here + cost_to_goal

        # ================
        # Abort Searching?
        # ================
        if f_cost >= threshold:
            return (f_cost, False)

        # Are we done?
        if cost_to_goal <= self.max_depth and self.search_complete(lt_state, steps_to_here):
            self.ida_nodes[lt_state] = steps_to_here
            return (f_cost, True)

        # If we have already explored the exact same scenario down another branch
        # then we can stop looking down this branch
        explored_cost_to_here = self.explored.get(lt_state, 99)
        if explored_cost_to_here <= cost_to_here:
            return (f_cost, False)
        self.explored[lt_state] = cost_to_here

        #self.ida_nodes[lt_state] = steps_to_here
        skip_other_steps_this_face = None

        for step in self.steps_not_on_same_face_and_layer[prev_step]:

            # https://github.com/cs0x7f/TPR-4x4x4-Solver/issues/7
            '''
            Well, it's a simple technique to reduce the number of nodes accessed.
            For example, we start at a position S whose pruning value is no more
            than maxl, otherwise, S will be pruned in previous searching.  After
            a move X, we obtain position S', whose pruning value is larger than
            maxl, which means that X makes S farther from the solved state.  In
            this case, we won't try X2 and X'.
            --cs0x7f
            '''
            if skip_other_steps_this_face is not None:
                if self.steps_on_same_face_and_layer_cache[(skip_other_steps_this_face, step)]:
                    continue
                else:
                    skip_other_steps_this_face = None

            self.parent.state = self.rotate_xxx(prev_state, step)

            (f_cost_tmp, found_solution) = self.ida_search(steps_to_here + [step,], threshold, step, self.parent.state[:])
            if found_solution:
                return (f_cost_tmp, True)
            else:
                if f_cost_tmp > threshold:
                    skip_other_steps_this_face = step
                else:
                    skip_other_steps_this_face = None

        self.parent.state = prev_state[:]
        return (f_cost, False)

    def recolor(self):

        if self.nuke_corners or self.nuke_edges or self.nuke_centers or self.recolor_positions:
            log.info("%s: recolor" % self)
            #self.parent.print_cube()

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

            #self.parent.print_cube()
            #sys.exit(0)

    def get_best_ida_solution(self, threshold):
        states_to_find = sorted(self.ida_nodes.keys())

        if states_to_find:

            # Uncomment to write states_to_find to a file so we can perf test via utils/binary-search-lookup.py
            #with open('states_to_find.txt', 'w') as fh:
            #    for x in states_to_find:
            #        fh.write(x + "\n")
            #log.info("wrote to states_to_find.txt")
            results = self.binary_search_multiple(states_to_find)

            if results:
                num_results = len(results.keys())
                log.info("%s: %d/%d states found" % (self, num_results, len(states_to_find)))
                #log.info("%s: results\n%s" % (self, pformat(results)))
                original_solution_len = len(self.original_solution)

                for (index, (lt_state, steps)) in enumerate(results.items()):
                    steps_to_here = self.ida_nodes[lt_state]

                    if self.search_complete(lt_state, steps_to_here):
                        this_solution = self.parent.solution[original_solution_len:]
                        this_solution_len = self.parent.get_solution_len_minus_rotates(this_solution)
                        log.info("%s: %d/%d solution_len %s" % (self, index+1, num_results, this_solution_len))
                        return this_solution

                return None
            else:
                log.info("%s: 0/%d states found" % (self, len(states_to_find)))
                return None
        else:
            return None

    def solve(self, min_ida_threshold=None, max_ida_threshold=99):
        """
        The goal is to find a sequence of moves that will put the cube in a state that is
        in our lookup table
        """

    # uncomment to cProfile solve()
        '''
        pass

    def solve(self, min_ida_threshold=None, max_ida_threshold=99):
            profile.runctx('self.solve_with_cprofile()', globals(), locals())

    def solve_with_cprofile(self, min_ida_threshold=None, max_ida_threshold=99):
        '''

        if self.parent.size == 2:
            from rubikscubennnsolver.RubiksCube222 import rotate_222
            self.rotate_xxx = rotate_222
        elif self.parent.size == 4:
            from rubikscubennnsolver.RubiksCube444 import rotate_444
            self.rotate_xxx = rotate_444
        elif self.parent.size == 5:
            from rubikscubennnsolver.RubiksCube555 import rotate_555
            self.rotate_xxx = rotate_555
        elif self.parent.size == 6:
            from rubikscubennnsolver.RubiksCube666 import rotate_666
            self.rotate_xxx = rotate_666
        elif self.parent.size == 7:
            from rubikscubennnsolver.RubiksCube777 import rotate_777
            self.rotate_xxx = rotate_777
        else:
            raise ImplementThis("Need rotate_xxx" % (self.parent.size, self.parent.size, self.parent.size))

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
            #log.info("%s: verify we can avoid OLL via moves %s" % (self, " ".join(self.moves_all)))
            for step in self.moves_all:
                if "w" in step and not step.endswith("2"):
                    log.info("%s: has avoid_oll %s" % (self, pformat(self.avoid_oll)))
                    break
            else:
                raise Exception("%s: has avoid_oll %s but there are no quarter wide turns among moves_all %s" % (
                    self, pformat(self.avoid_oll), " ".join(self.moves_all)))

        # Get the intial cube state and cost_to_goal
        (state, cost_to_goal) = self.ida_heuristic()

        # The cube is already in the desired state, nothing to do
        if self.search_complete(state, []):
            log.info("%s: cube state %s is in our lookup table" % (self, state))
            tmp_solution = self.parent.solution[:]
            self.parent.state = self.pre_recolor_state[:]
            self.parent.solution = self.pre_recolor_solution[:]

            for step in tmp_solution[len(self.original_solution):]:
                self.parent.rotate(step)

            return True

        # If we are here (odds are very high we will be) it means that the current
        # cube state was not in the lookup table.  We must now perform an IDA search
        # until we find a sequence of moves that takes us to a state that IS in the
        # lookup table.
        if min_ida_threshold is None:
            min_ida_threshold = cost_to_goal

        # If this is the case the range loop below isn't worth running
        if min_ida_threshold >= max_ida_threshold+1:
            raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))

        start_time0 = dt.datetime.now()
        #log.info("%s: using moves %s" % (self, pformat(self.moves_all)))
        log.info("%s: IDA threshold range %d->%d" % (self, min_ida_threshold, max_ida_threshold))
        total_ida_count = 0

        for threshold in range(min_ida_threshold, max_ida_threshold+1):
            steps_to_here = []
            start_time1 = dt.datetime.now()
            self.ida_count = 0
            self.explored = {}
            self.ida_nodes = {}

            self.ida_search(steps_to_here, threshold, None, self.original_state[:])
            total_ida_count += self.ida_count
            best_solution = self.get_best_ida_solution(threshold)

            if best_solution:

                if self.collect_stats:
                    self.parent.state = self.original_state[:]
                    self.parent.solution = self.original_solution[:]
                    steps_to_go = len(best_solution)

                    heuristic_tuple = self.ida_heuristic_tuple()

                    if heuristic_tuple not in self.parent.heuristic_stats:
                        self.parent.heuristic_stats[heuristic_tuple] = []
                    self.parent.heuristic_stats[heuristic_tuple].append(steps_to_go)
                    hit_wtf = False
                    prev_step = None
                    max_index = len(best_solution) - 1

                    for (index, step) in enumerate(best_solution):
                        self.parent.rotate(step)
                        steps_to_go -= 1
                        heuristic_tuple = self.ida_heuristic_tuple()

                        if heuristic_tuple not in self.parent.heuristic_stats:
                            self.parent.heuristic_stats[heuristic_tuple] = []

                        #if steps_to_go < max(heuristic_tuple):
                        #    log.info("%s: index %d, steps_to_go %d, step %s, heuristic_tuple %s, best_solution %s, WTF??" %\
                        #        (self, index, steps_to_go, step, pformat(heuristic_tuple), pformat(best_solution)))
                        #    hit_wtf = True
                        #else:
                        #    log.info("%s: index %d, steps_to_go %d, step %s, heuristic_tuple %s, best_solution %s" % (self, index, steps_to_go, step, pformat(heuristic_tuple), pformat(best_solution)))

                        #self.parent.print_cube()
                        self.parent.heuristic_stats[heuristic_tuple].append(steps_to_go)

                self.parent.state = self.pre_recolor_state[:]
                self.parent.solution = self.pre_recolor_solution[:]

                for step in best_solution:
                    self.parent.rotate(step)

                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d nodes in %s (%s total)" %
                    (self, threshold, self.ida_count,
                     pretty_time(end_time1 - start_time1),
                     pretty_time(end_time1 - start_time0)))
                delta = end_time1 - start_time0
                nodes_per_sec = int(total_ida_count / delta.total_seconds())
                log.info("%s: IDA explored %d nodes in %s, %d nodes-per-sec" % (self, total_ida_count, delta, nodes_per_sec))
                log.info("%s: IDA found %d step solution %s" % (self, len(best_solution), " ".join(best_solution)))
                self.explored = {}
                self.ida_nodes = {}
                gc.collect()
                return True
            else:
                end_time1 = dt.datetime.now()
                delta = end_time1 - start_time1
                nodes_per_sec = int(self.ida_count / delta.total_seconds())
                log.info("%s: IDA threshold %d, explored %d nodes in %s, %d nodes-per-sec" %
                    (self, threshold, self.ida_count, pretty_time(delta), nodes_per_sec))

        log.info("%s: could not find a solution via IDA with max threshold of %d " % (self, max_ida_threshold))
        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]
        raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))



class LookupTableIDAViaC(object):

    def __init__(self, parent, files, C_ida_type):
        self.avoid_oll = None
        self.avoid_pll = False
        self.nuke_corners = False
        self.nuke_edges = False
        self.nuke_centers = False
        self.recolor_positions = []
        self.parent = parent
        self.C_ida_type = C_ida_type

        for (filename, filesize, md5target) in files:
            #log.info("%s: rm_file_if_mismatch %s begin" % (self, filename))
            rm_file_if_mismatch(filename, filesize, md5target)
            #log.info("%s: rm_file_if_mismatch %s end" % (self, filename))
            #log.info("%s: download_file_if_needed %s begin" % (self, filename))
            download_file_if_needed(filename, self.parent.size)
            #log.info("%s: download_file_if_needed %s end\n" % (self, filename))

    def __str__(self):
        return self.__class__.__name__

    def recolor(self):

        if self.nuke_corners or self.nuke_edges or self.nuke_centers or self.recolor_positions:
            log.info("%s: recolor" % self)
            #self.parent.print_cube()

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

            #self.parent.print_cube()
            #sys.exit(0)

    def solve(self):

        # If this is a lookup table that is staging a pair of colors (such as U and D)
        # then recolor the cubies accordingly.
        self.pre_recolor_state = self.parent.state[:]
        self.pre_recolor_solution = self.parent.solution[:]
        self.recolor()

        if not os.path.isfile("ida_search"):
            log.info("ida_search is missing...compiling it now")
            subprocess.check_output("gcc -O3 -o ida_search ida_search_core.c ida_search.c rotate_xxx.c ida_search_444.c ida_search_555.c ida_search_666.c ida_search_777.c xxhash.c -lm".split())

        kociemba_string = self.parent.get_kociemba_string(True)
        cmd = ["./ida_search", "--kociemba", kociemba_string, "--type", self.C_ida_type]

        if self.avoid_oll is not None:
            orbits_with_oll = self.parent.center_solution_leads_to_oll_parity()

            if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
                # Edge parity is currently odd so we need an odd number of w turns in orbit 0
                if 0 in orbits_with_oll:
                    cmd.append("--orbit0-need-odd-w")

                # Edge parity is currently even so we need an even number of w turns in orbit 0
                else:
                    cmd.append("--orbit0-need-even-w")

            if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
                # Edge parity is currently odd so we need an odd number of w turns in orbit 1
                if 1 in orbits_with_oll:
                    cmd.append("--orbit1-need-odd-w")

                # Edge parity is currently even so we need an even number of w turns in orbit 1
                else:
                    cmd.append("--orbit1-need-even-w")

            if self.avoid_oll != 0 and self.avoid_oll != 1 and self.avoid_oll != (0, 1):
                raise Exception("avoid_oll is only supported for orbits 0 or 1, not {}".format(self.avoid_oll))

        if self.parent.cpu_mode == "fast":
            cmd.append("--fast")
        elif self.parent.cpu_mode == "normal":
            cmd.append("--normal")
        elif self.parent.cpu_mode == "slow":
            cmd.append("--slow")
        else:
            raise Exception("%s: What CPU mode for %s?" % (self, self.parent))

        if self.avoid_pll:
            # To avoid PLL the odd/even of edge swaps and corner swaps must agree...they
            # must both be odd or both be even. In order to avoid OLL though (which we
            # should have already done) the edge swaps must be even.
            assert self.parent.size == 4, "avoid_pll should only be True for 4x4x4 cubes"
            cmd.append("--avoid-pll")

        log.info("%s: solving via C ida_search\n\n%s" % (self, " ".join(cmd)))
        output = subprocess.check_output(cmd).decode('ascii')
        log.info("\n\n" + output + "\n\n")

        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                steps = line.split(":")[1].strip().split()
                break
        else:
            raise NoIDASolution("%s" % self)

        log.info("%s: ida_search found solution %s" % (self, ' '.join(steps)))
        self.parent.state = self.pre_recolor_state[:]
        self.parent.solution = self.pre_recolor_solution[:]

        for step in steps:
            self.parent.rotate(step)


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
