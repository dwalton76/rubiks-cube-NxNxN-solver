#!/usr/bin/env python3

import datetime as dt
from rubikscubennnsolver.RubiksSide import SolveError
from pprint import pformat
from pyhashxx import hashxx
from subprocess import call
import logging
import os
import sys


log = logging.getLogger(__name__)


class ImplementThis(Exception):
    pass


class NoSteps(Exception):
    pass


class NoIDASolution(Exception):
    pass


def get_characters_common_count(strA, strB, start_index):
    """
    This assumes strA and strB are the same length
    """
    result = 0

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

    >>> steps_on_same_face_and_layer("3Uw2", "3Uw")
    True

    >>> steps_on_same_face_and_layer("Uw2", "3Uw")
    False
    """
    if prev_step is None:
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


class LookupTable(object):

    def __init__(self, parent, filename, state_target, linecount, max_depth=None, filesize=None):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.filename = filename
        self.filename_gz = filename + '.gz'
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.filename_exists = False
        self.linecount = linecount
        self.max_depth = max_depth
        self.avoid_oll = False
        self.avoid_pll = False
        self.preloaded_state_set = False
        self.preloaded_cache = False
        self.ida_all_the_way = False
        self.use_lt_as_prune = False
        self.fh_txt_seek_calls = 0
        self.cache = {}
        self.filesize = filesize

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"

        if 'dummy' not in self.filename:
            assert self.linecount, "%s linecount is %s" % (self, self.linecount)

        # This only happens if a new copy of the lookup table has been checked in...we need to delete
        # the one we have and download the new one.
        if os.path.exists(self.filename) and self.filesize is not None and os.path.getsize(self.filename) != self.filesize:
            log.info("%s: filesize %s does not equal target filesize %s" % (self, os.path.getsize(self.filename), self.filesize))
            os.remove(self.filename)

            if os.path.exists(self.filename_gz):
                os.remove(self.filename_gz)

        if not os.path.exists(self.filename):
            if not os.path.exists(self.filename_gz):
                url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/%s" % (self.parent.size, self.parent.size, self.parent.size, self.filename_gz)
                log.info("Downloading table via 'wget %s'" % url)
                call(['wget', url])

            log.warning("gunzip %s" % self.filename_gz)
            call(['gunzip', self.filename_gz])

        # Find the state_width for the entries in our .txt file
        with open(self.filename, 'r') as fh:
            first_line = next(fh)
            self.width = len(first_line)
            (state, steps) = first_line.split(':')
            self.state_width = len(state)

        self.hex_format = '%' + "0%dx" % self.state_width
        self.filename_exists = True

        if isinstance(state_target, tuple):
            self.state_target = set(state_target)
        elif isinstance(state_target, list):
            self.state_target = set(state_target)
        else:
            self.state_target = set((state_target, ))

        # 'rb' mode is about 3x faster than 'r' mode
        self.fh_txt = open(self.filename, mode='rb')

    def __str__(self):
        return self.desc

    def binary_search(self, state_to_find):
        first = 0
        last = self.linecount - 1
        b_state_to_find = bytearray(state_to_find, encoding='utf-8')

        while first <= last:
            midpoint = int((first + last)/2)
            self.fh_txt.seek(midpoint * self.width)
            self.fh_txt_seek_calls += 1

            # Only read the 'state' part of the line (for speed)
            b_state = self.fh_txt.read(self.state_width)

            if b_state_to_find < b_state:
                last = midpoint - 1

            # If this is the line we are looking for, then read the entire line
            elif b_state_to_find == b_state:
                self.fh_txt.seek(midpoint * self.width)
                line = self.fh_txt.read(self.width)
                return line.decode('utf-8').rstrip()

            else:
                first = midpoint + 1

        return None

    def preload_cache(self):
        log.warning("%s: begin preload cache" % self)

        if isinstance(self, LookupTableCostOnly):
            raise Exception("%s is a CostOnly table, no need to call preload_cache()" % self)

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

        self.preloaded_cache = True
        log.warning("{}: end preload cache ({:,} bytes)".format(self, sys.getsizeof(self.cache)))

    def steps(self, state_to_find=None):
        """
        Return a list of the steps found in the lookup table for the current cube state
        """
        if state_to_find is None:
            state_to_find = self.state()

        # If we are at one of our state_targets we do not need to do anything
        if state_to_find in self.state_target:
            return None

        if self.preloaded_cache:
            steps = self.cache.get(state_to_find)
            if steps:
                return steps.split()
            else:
                return None

        line = self.binary_search(state_to_find)

        if line:
            (state, steps) = line.strip().split(':')
            steps_list = steps.split()
            return steps_list

        else:
            return None

    def steps_cost(self, state_to_find=None):

        if state_to_find is None:
            state_to_find = self.state()

        steps = self.steps(state_to_find)

        if steps is None:
            #log.info("%s: steps_cost None for %s (stage_target)" % (self, state_to_find))
            return 0
        else:
            if steps[0].isdigit():
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
            state = self.state()

            if tbd:
                log.info("%s: solve() state %s vs state_target %s" % (self, state, pformat(self.state_target)))

            if state in self.state_target:
                break

            steps = self.steps(state)

            if steps:
                #log.info("%s: PRE solve() state %s found %s" % (self, state, ' '.join(steps)))
                #self.parent.print_cube()
                #log.info("%s: %d steps" % (self, len(steps)))

                for step in steps:
                    self.parent.rotate(step)

                #log.info("%s: POST solve()" % self)
                #self.parent.print_cube()

            else:
                self.parent.print_cube()
                raise NoSteps("%s: state %s does not have steps" % (self, state))

    def heuristic(self):
        pt_state = self.state()

        if pt_state in self.state_target:
            return 0

        else:
            pt_steps_cost = self.steps_cost(pt_state)

            if pt_steps_cost:
                return pt_steps_cost

            elif self.max_depth:
                # This is the exception to the rule but some prune tables such
                # as lookup-table-6x6x6-step23-UD-oblique-edge-pairing-LFRB-only.txt
                # are partial tables so use the max_depth of the table +1
                return self.max_depth + 1

        self.parent.print_cube()
        raise SolveError("%s does not have max_depth and does not have steps for %s, state_width %d" % (self, pt_state, self.state_width))


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


class LookupTableCostOnly(LookupTable):

    def __init__(self, parent, filename, state_target, linecount, max_depth=None, load_string=True, filesize=None):
        self.parent = parent
        self.sides_all = (self.parent.sideU, self.parent.sideL, self.parent.sideF, self.parent.sideR, self.parent.sideB, self.parent.sideD)
        self.filename = filename
        self.filename_gz = filename + '.gz'
        self.desc = filename.replace('lookup-table-', '').replace('.txt', '')
        self.filename_exists = False
        self.linecount = linecount
        self.max_depth = max_depth
        self.avoid_oll = False
        self.avoid_pll = False
        self.preloaded_state_set = False
        self.preloaded_cache = False
        self.ida_all_the_way = False
        self.use_lt_as_prune = False
        self.filesize = filesize

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"

        if 'dummy' not in self.filename:
            assert self.linecount, "%s linecount is %s" % (self, self.linecount)

        # This only happens if a new copy of the lookup table has been checked in...we need to delete
        # the one we have and download the new one.
        if os.path.exists(self.filename) and self.filesize is not None and os.path.getsize(self.filename) != self.filesize:
            log.info("%s: filesize %s does not equal target filesize %s" % (self, os.path.getsize(self.filename), self.filesize))
            os.remove(self.filename)

            if os.path.exists(self.filename_gz):
                os.remove(self.filename_gz)

        if not os.path.exists(self.filename):
            if not os.path.exists(self.filename_gz):
                url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/%s" % (self.parent.size, self.parent.size, self.parent.size, self.filename_gz)
                log.info("Downloading table via 'wget %s'" % url)
                call(['wget', url])

            log.warning("gunzip %s" % self.filename_gz)
            call(['gunzip', self.filename_gz])

        self.filename_exists = True

        if isinstance(state_target, tuple):
            self.state_width = len(state_target[0])
            self.state_target = set(state_target)
        elif isinstance(state_target, list):
            self.state_width = len(state_target[0])
            self.state_target = set(state_target)
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
        if load_string:

            log.warning("%s: begin preload cost-only" % self)
            with open(self.filename, 'r') as fh:
                for line in fh:
                    self.content = line
            self.fh_txt_seek_calls += 1
            log.warning("{}: end preload cost-only ({:,} bytes)".format(self, sys.getsizeof(self.content)))
        else:
            # 'rb' mode is about 3x faster than 'r' mode
            self.fh_txt = open(self.filename, mode='rb')
            self.content = None

    def steps_cost(self, state_to_find=None):

        if state_to_find is None:
            state_to_find = self.state()

        # state_to_find is an integer, there is a one byte hex character in the file for each possible state.
        # This hex character is the number of steps required to solve the corresponding state.
        if self.content is None:
            self.fh_txt.seek(state_to_find)
            result = int(self.fh_txt.read(1).decode('utf-8'), 16)

            #if result == 0:
            #    raise Exception("%s: table is hosed...result for %d is 0" % (self, state_to_find))

            self.fh_txt_seek_calls += 1
            return result

        else:
            return int(self.content[state_to_find], 16)


class LookupTableHashCostOnly(LookupTableCostOnly):

    def __init__(self, parent, filename, state_target, linecount, max_depth=None, load_string=True, bucketcount=None):
        LookupTableCostOnly.__init__(self, parent, filename, state_target, linecount, max_depth, load_string)
        self.bucketcount = bucketcount

    def steps_cost(self, state_to_find=None):

        if state_to_find is None:
            state_to_find = self.state()

        # compute the hash_index for state_to_find, look that many bytes into the
        # file/self.conten and retrieve a single hex character. This hex character
        # is the number of steps required to solve the corresponding state.
        hash_raw = hashxx(state_to_find.encode('utf-8'))
        hash_index = int(hash_raw % self.bucketcount)

        if self.content is None:
            self.fh_txt.seek(hash_index)
            result = int(self.fh_txt.read(1).decode('utf-8'), 16)
            self.fh_txt_seek_calls += 1
            return result

        else:
            return int(self.content[hash_index], 16)


class LookupTableIDA(LookupTable):

    def __init__(self, parent, filename, state_target, moves_all, moves_illegal, prune_tables, linecount, max_depth=None, filesize=None):
        LookupTable.__init__(self, parent, filename, state_target, linecount, max_depth, filesize)
        self.prune_tables = prune_tables

        for x in moves_illegal:
            if x not in moves_all:
                raise Exception("illegal move %s is not in the list of legal moves" % x)

        self.moves_all = []
        for x in moves_all:
            if x not in moves_illegal:
                self.moves_all.append(x)

    def ida_heuristic_total(self):
        total = 0

        for pt in self.prune_tables:
            total += pt.heuristic()

        return total

    def ida_heuristic(self):
        cost_to_goal = 0

        if self.use_lt_as_prune:
            state = self.state()

            # If we are at our target then our cost_to_goal is 0
            if state in self.state_target:
                return cost_to_goal

            steps = self.steps(state)

            if steps is None:
                assert self.max_depth is not None, "%s: use_lt_as_prune is True but max_depth is not set" % self
                cost_to_goal = self.max_depth + 1
            else:
                cost_to_goal = len(steps)

        for pt in self.prune_tables:

            # If there is no way this pt will have a higher cost than the prune
            # tables we have already examined do not bother looking up the cost
            # for this pt
            if cost_to_goal >= pt.max_depth:
                continue

            pt_cost_to_goal = pt.heuristic()

            if pt_cost_to_goal > cost_to_goal:
                cost_to_goal = pt_cost_to_goal

        return cost_to_goal

    def search_complete(self, state, steps_to_here):

        if self.ida_all_the_way:
            if state not in self.state_target:
                return False
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
            self.parent.rotate(step)

        for step in steps:
            self.parent.rotate(step)

        # The cube is now in a state where it is in the lookup table, we may need
        # to do several lookups to get to our target state though. Use
        # LookupTabele's solve() to take us the rest of the way to the target state.
        LookupTable.solve(self)

        if self.avoid_oll and self.parent.center_solution_leads_to_oll_parity():
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
        cost_to_goal = self.ida_heuristic()
        f_cost = cost_to_here + cost_to_goal

        lt_state = self.state()

        # If our cost_to_goal is greater than the max_depth of our main lookup table then there is no
        # need to do a binary search through the main lookup table to look for our current state...this
        # saves us some disk IO
        if (cost_to_goal <= self.max_depth and
            self.search_complete(lt_state, steps_to_here)):
            log.info("%s: %d seek calls" % (self, self.fh_txt_seek_calls))
            self.fh_txt_seek_calls = 0

            for pt in self.prune_tables:
                log.info("%s: %d seek calls" % (pt, pt.fh_txt_seek_calls))
                pt.fh_txt_seek_calls = 0

            log.info("%s: IDA found match %d steps in %s, lt_state %s, f_cost %d (%d + %d)" %
                     (self, len(steps_to_here), ' '.join(steps_to_here), lt_state, f_cost, cost_to_here, cost_to_goal))
            return (f_cost, True)

        # ================
        # Abort Searching?
        # ================
        if f_cost >= threshold:
            return (f_cost, False)

        # If we have already explored the exact same scenario down another branch
        # then we can stop looking down this branch
        explored_cost_to_here = self.explored.get(lt_state)

        if explored_cost_to_here is not None and explored_cost_to_here <= cost_to_here:
            return (f_cost, False)
        self.explored[lt_state] = cost_to_here
        skip_other_steps_this_face = None

        # log.info("moves_all %s" % ' '.join(self.moves_all))
        for step in self.moves_all:

            #if steps_cancel_out(prev_step, step):
            #    continue

            if steps_on_same_face_and_layer(prev_step, step):
                continue

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
                if steps_on_same_face_and_layer(skip_other_steps_this_face, step):
                    continue
                else:
                    skip_other_steps_this_face = None

            self.parent.state = self.rotate_xxx(prev_state[:], step)

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

    def solve(self, min_ida_threshold=None, max_ida_threshold=99):
        """
        The goal is to find a sequence of moves that will put the cube in a state that is
        in our lookup table
        """
        start_time0 = dt.datetime.now()

        # save cube state
        self.original_state = self.parent.state[:]
        self.original_solution = self.parent.solution[:]

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

        state = self.state()
        #log.info("%s: ida_stage() state %s vs state_target %s" % (self, state, self.state_target))

        # The cube is already in the desired state, nothing to do
        if state in self.state_target or self.search_complete(state, []):
            log.info("%s: cube is already at the target state %s" % (self, state))
            return True

        # The cube is already in a state that is in our lookup table, nothing for IDA to do
        steps = self.steps(state)

        if steps:
            log.info("%s: cube is already in a state %s that is in our lookup table" % (self, state))

            # The cube is now in a state where it is in the lookup table, we may need
            # to do several lookups to get to our target state though. Use
            # LookupTabele's solve() to take us the rest of the way to the target state.
            LookupTable.solve(self)

            if self.avoid_oll and self.parent.center_solution_leads_to_oll_parity():
                log.info("%s: but the current state leads to OLL so we must IDA" % self)
                self.parent.state = self.original_state[:]
                self.parent.solution = self.original_solution[:]
            else:
                return True

        # If we are here (odds are very high we will be) it means that the current
        # cube state was not in the lookup table.  We must now perform an IDA search
        # until we find a sequence of moves that takes us to a state that IS in the
        # lookup table.

        if min_ida_threshold is None:
            min_ida_threshold = self.ida_heuristic()

        # If this is the case the range loop below isn't worth running
        if min_ida_threshold >= max_ida_threshold+1:
            raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))

        log.info("%s: IDA threshold range %d->%d" % (self, min_ida_threshold, max_ida_threshold))
        total_ida_count = 0

        for threshold in range(min_ida_threshold, max_ida_threshold+1):
            steps_to_here = []
            start_time1 = dt.datetime.now()
            self.ida_count = 0
            self.explored = {}

            (f_cost, found_solution) = self.ida_search(steps_to_here, threshold, None, self.original_state[:])
            total_ida_count += self.ida_count

            if found_solution:
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d nodes, took %s (%s total)" %
                    (self, threshold, self.ida_count,
                     pretty_time(end_time1 - start_time1),
                     pretty_time(end_time1 - start_time0)))
                delta = end_time1 - start_time0
                nodes_per_sec = int(total_ida_count / delta.total_seconds())
                log.info("%s: IDA explored %d nodes in %s, %d nodes-per-sec" % (self, total_ida_count, delta, nodes_per_sec))
                return True
            else:
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d nodes, took %s" %
                    (self, threshold, self.ida_count, pretty_time(end_time1 - start_time1)))

        # The only time we will get here is when max_ida_threshold is a low number.  It will be up to the caller to:
        # - 'solve' one of their prune tables to put the cube in a state that we can find a solution for a little more easily
        # - call ida_solve() again but with a near infinite max_ida_threshold...99 is close enough to infinity for IDA purposes
        log.info("%s: could not find a solution via IDA with max threshold of %d " % (self, max_ida_threshold))

        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
