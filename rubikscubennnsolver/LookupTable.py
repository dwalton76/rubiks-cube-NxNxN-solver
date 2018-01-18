#!/usr/bin/env python3

import datetime as dt
from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.rotate_xxx import rotate_222, rotate_444, rotate_555, rotate_666, rotate_777
from rubikscubennnsolver import reverse_steps
from subprocess import check_output
import json
import logging
import math
import os
import shutil
import subprocess
import sys


log = logging.getLogger(__name__)


class ImplementThis(Exception):
    pass


class NoSteps(Exception):
    pass


class NoIDASolution(Exception):
    pass


class NoAStarSolution(Exception):
    pass


def get_characters_common_count(strA, strB, start_index):
    """
    This assumes strA and strB are the same length
    """
    result = 0

    try:
        for index in range(start_index, len(strA)):
            if strA[index] == strB[index]:
                result += 1
    except IndexError:
        log.info("strA: %s" % strA)
        log.info("strB: %s" % strB)
        log.info("start_index: %s" % start_index)
        raise

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
    if prev_step.endswith("'"):
        prev_step = prev_step[:-1]

    if step.endswith("'"):
        step = step[:-1]

    # chop the trailing 2
    if prev_step.endswith("2"):
        prev_step = prev_step[:-1]

    if step.endswith("2"):
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

    def __init__(self, parent, filename, state_target, linecount, max_depth=None):
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
        self.preloaded_cache = False
        self.preloaded_state_set = False
        self.ida_all_the_way = False

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"

        if 'dummy' not in self.filename:
            assert self.linecount, "%s linecount is %s" % (self, self.linecount)

        if not os.path.exists(self.filename):
            if not os.path.exists(self.filename_gz):

                # Special cases where I could not get them one under 100M so I split it via:
                # split -b 40m foo.txt.gz "foo.txt.gz.part-"

                # =====
                # 4x4x4
                # =====
                if self.filename_gz == 'lookup-table-4x4x4-step71-tsai-phase3-edges.txt.gz':

                    # Download all parts
                    for extension in ('aa', 'ab', 'ac', 'ad'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step71-tsai-phase3-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    # cat them together into a .gz file
                    subprocess.call('cat lookup-table-4x4x4-step71-tsai-phase3-edges.txt.gz.part-* > lookup-table-4x4x4-step71-tsai-phase3-edges.txt.gz', shell=True)

                    # remove all of the parts
                    for extension in ('aa', 'ab', 'ac', 'ad'):
                        os.unlink('lookup-table-4x4x4-step71-tsai-phase3-edges.txt.gz.part-%s' % extension)

                elif self.filename_gz == 'lookup-table-4x4x4-step100-edges.txt.gz':

                    # Download all parts
                    for extension in ('aa', 'ab', 'ac'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step100-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    # cat them together into a .gz file
                    subprocess.call('cat lookup-table-4x4x4-step100-edges.txt.gz.part-* > lookup-table-4x4x4-step100-edges.txt.gz', shell=True)

                    # remove all of the parts
                    for extension in ('aa', 'ab', 'ac'):
                        os.unlink('lookup-table-4x4x4-step100-edges.txt.gz.part-%s' % extension)

                # =====
                # 5x5x5
                # =====
                elif self.filename_gz == 'lookup-table-4x4x4-step50-tsai-phase1.txt.gz':

                    # Download all three parts
                    for extension in ('aa', 'ab', 'ac'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step50-tsai-phase1.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    # cat them together into a .gz file
                    subprocess.call('cat lookup-table-4x4x4-step50-tsai-phase1.txt.gz.part-* > lookup-table-4x4x4-step50-tsai-phase1.txt.gz', shell=True)

                    # remove all of the parts
                    os.unlink('lookup-table-4x4x4-step50-tsai-phase1.txt.gz.part-aa')
                    os.unlink('lookup-table-4x4x4-step50-tsai-phase1.txt.gz.part-ab')
                    os.unlink('lookup-table-4x4x4-step50-tsai-phase1.txt.gz.part-ac')

                # =====
                # 6x6x6
                # =====
                elif self.filename_gz == 'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz':

                    # Download all three parts
                    for extension in ('aa', 'ab'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    # cat them together into a .gz file
                    subprocess.call('cat lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-* > lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz', shell=True)

                    # remove all of the parts
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-aa')
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-ab')

                # =====
                # 7x7x7
                # =====
                elif self.filename_gz == 'lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt.gz':

                    # Download all parts
                    for extension in ('aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    # cat them together into a .gz file
                    subprocess.call('cat lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt.gz.part-* > lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt.gz', shell=True)

                    # remove all of the parts
                    for extension in ('aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak'):
                        os.unlink('lookup-table-7x7x7-step80-LFRB-solve-inner-center-and-oblique-edges.txt.gz.part-%s' % extension)
                else:
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/%s" % (self.parent.size, self.parent.size, self.parent.size, self.filename_gz)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

            log.warning("gunzip %s" % self.filename_gz)
            subprocess.call(['gunzip', self.filename_gz])

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

        self.cache = {}

        # 'rb' mode is about 3x faster than 'r' mode
        self.fh_txt = open(self.filename, mode='rb')

    def __str__(self):
        return self.desc

    def preload_cache(self):
        """
        This is experimental, it would typically be used to load the
        contents of a prune table. For solving one cube it probably
        doesn't buy you much but if one were to make a daemon that
        loads all of the prune tables up front (that would take a lot
        of memory) it might be worth it then.
        """
        log.info("%s: preload_cache start" % self)

        self.cache = {}
        for line in self.fh_txt:
            (state, steps) = line.decode('utf-8').rstrip().split(':')
            self.cache[state] = steps.split()

        log.info("%s: preload_cache end" % self)
        self.preloaded_cache = True

    def preload_state_set(self):
        """
        This is experimental, it would typically be used to load only the keys
        of an IDA lookup table. This would allow you to avoid doing a binary
        search of the huge IDA lookup tables for keys that are not there.
        """
        log.info("%s: preload_state_set start" % self)

        self.state_set = set()
        for line in self.fh_txt:
            (state, _) = line.decode('utf-8').strip().split(':')
            self.state_set.add(state)

        log.info("%s: preload_state_set end" % self)
        self.preloaded_state_set = True

    def binary_search(self, state_to_find):
        first = 0
        last = self.linecount - 1
        b_state_to_find = bytearray(state_to_find, encoding='utf-8')

        while first <= last:
            midpoint = int((first + last)/2)
            self.fh_txt.seek(midpoint * self.width)

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
            return self.cache.get(state_to_find)

        elif self.preloaded_state_set:

            if state_to_find in self.state_set:
                line = self.binary_search(state_to_find)

                if line:
                    (state, steps) = line.strip().split(':')
                    return steps.split()
                else:
                    raise Exception("should not be here")
            else:
                return None

        else:
            try:
                return self.cache[state_to_find]
            except KeyError:

                line = self.binary_search(state_to_find)

                if line:
                    (state, steps) = line.strip().split(':')
                    steps_list = steps.split()
                    self.cache[state_to_find] = steps_list
                    return steps_list

                else:
                    self.cache[state_to_find] = None
                    return None

    def steps_cost(self, state_to_find=None):

        if state_to_find is None:
            state_to_find = self.state()

        steps = self.steps(state_to_find)

        if steps is None:
            #log.info("%s: steps_cost None for %s (stage_target)" % (self, state_to_find))
            return 0
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
        pt_steps = self.steps(pt_state)

        if pt_state in self.state_target:
            len_pt_steps = 0

        elif pt_steps:
            len_pt_steps = len(pt_steps)

            # There are few prune tables that I built where instead of listing the steps
            # for a state I just listed how many steps there would be.  I did this to save
            # space.  lookup-table-5x5x5-step13-UD-centers-stage-UFDB-only.txt is one such table.
            if len_pt_steps == 1 and pt_steps[0].isdigit():
                len_pt_steps = int(pt_steps[0])

        elif self.max_depth:
            # This is the exception to the rule but some prune tables such
            # as lookup-table-6x6x6-step23-UD-oblique-edge-pairing-LFRB-only.txt
            # are partial tables so use the max_depth of the table +1
            len_pt_steps = self.max_depth + 1

        else:
            self.parent.print_cube()
            raise SolveError("%s does not have max_depth and does not have steps for %s, state_width %d" % (self, pt_state, self.state_width))

        return len_pt_steps

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

        This is only used by the 4x4x4 and 5x5x5 edges tables
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


class LookupTableAStar(LookupTable):

    def __init__(self, parent, filename, state_target, moves_all, moves_illegal, prune_tables, linecount, max_depth=None):
        LookupTable.__init__(self, parent, filename, state_target, linecount, max_depth)
        self.prune_tables = prune_tables

        for x in moves_illegal:
            if x not in moves_all:
                raise Exception("illegal move %s is not in the list of legal moves" % x)

        self.moves_all = []
        for x in moves_all:
            if x not in moves_illegal:
                self.moves_all.append(x)

    def ida_heuristic(self, use_lt_as_prune=False):
        cost_to_goal = 0

        if use_lt_as_prune:
            state = self.state()
            steps = self.steps(state)

            if steps is None:
                assert self.max_depth is not None, "%s: use_lt_as_prune is True but max_depth is not set" % self
                cost_to_goal = self.max_depth + 1
            else:
                cost_to_goal = len(steps)

        for pt in self.prune_tables:
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
            log.info("%s: IDA found match but it leads to OLL" % self)
            return False

        if self.avoid_pll and self.parent.edge_solution_leads_to_pll_parity():
            self.parent.state = self.original_state[:]
            self.parent.solution = self.original_solution[:]
            log.info("%s: IDA found match but it leads to PLL" % self)
            return False

        return True

    def _solve(self):
        """
        solving prep work used by both AStar and IDA* solve()

        Returns True if cube is already "solved"
        """
        # save cube state
        self.original_state = self.parent.state[:]
        self.original_solution = self.parent.solution[:]

        if self.parent.size == 2:
            self.rotate_xxx = rotate_222
        elif self.parent.size == 4:
            self.rotate_xxx = rotate_444
        elif self.parent.size == 5:
            self.rotate_xxx = rotate_555
        elif self.parent.size == 6:
            self.rotate_xxx = rotate_666
        elif self.parent.size == 7:
            self.rotate_xxx = rotate_777
        else:
            raise ImplementThis("Need rotate_xxx" % (self.parent.size, self.parent.size, self.parent.size))

        state = self.state()
        #log.info("%s: ida_stage() state %s vs state_target %s" % (self, state, self.state_target))

        # The cube is already in the desired state, nothing to do
        if state in self.state_target:
            log.info("%s: IDA/AStar, cube is already at the target state %s" % (self, state))
            return True

        # The cube is already in a state that is in our lookup table, nothing for IDA to do
        steps = self.steps(state)

        if steps:
            log.info("%s: IDA/Star, cube is already in a state %s that is in our lookup table" % (self, state))

            # The cube is now in a state where it is in the lookup table, we may need
            # to do several lookups to get to our target state though. Use
            # LookupTabele's solve() to take us the rest of the way to the target state.
            LookupTable.solve(self)
            return True

        # If we are here (odds are very high we will be) it means that the current
        # cube state was not in the lookup table.  We must now perform an IDA search
        # until we find a sequence of moves that takes us to a state that IS in the
        # lookup table.
        return False

    def astar_search(self, solutions_target=None, max_depth=None):
        """
        This isn't used at the moment...I did it as an experiment.
        """
        import bisect
        from sortedcontainers import SortedList

        astar_countA = 0
        exploredA = {}
        solutions = []

        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        # Initialize workqA
        workqA = SortedList()
        workqA.append((0, 0, 0, [], self.original_state[:]))

        while workqA:
            astar_countA += 1

            # len_steps_to_here and cost_to_goal are just tie-breakers for sorting the
            # better step sequencs to the front of the workq

            # workq for going from scrambled to solved
            (f_costA, _, _, steps_to_hereA, prev_stateA) = workqA.pop(0)
            self.parent.state = prev_stateA[:]
            lt_stateA = self.state()

            use_search_complete = False
            #use_search_complete = True

            if use_search_complete:
                if self.search_complete(lt_stateA, steps_to_hereA):
                    log.info("%s: AStar found match %d steps in, %s, lt_state %s, AStar count %d, f_cost %d" %
                             (self, len(steps_to_hereA), ' '.join(steps_to_hereA), lt_stateA, astar_countA, f_costA))

                    if solutions_target is None:
                        return True
                    else:
                        cost_to_here = self.parent.get_solution_len_minus_rotates(steps_to_hereA)
                        cost_to_goal = self.parent.lt_tsai_phase2_centers.heuristic()
                        f_cost = cost_to_here + cost_to_goal

                        solution_tuple = (f_cost, cost_to_here, self.parent.solution[:])

                        if solution_tuple not in solutions:
                            solutions.append(solution_tuple)

                        if len(solutions) >= solutions_target:
                            return solutions

            else:
                # I used the following (instead of the search_complete() call above) to test
                # using A* to go all the way to our goal, in other words don't use the main
                # lookup table at all, only use the prune tables.
                #
                # This works but it is slower...for instance when solving 5x5x5 centers and
                # you stage the LR centers, using search_complete() takes 30ms but
                # using just the prune tables takes 44000ms .
                cost_to_goal = self.ida_heuristic()

                if cost_to_goal == 0:
                    # rotate_xxx() is very fast but it does not append the
                    # steps to the solution so put the cube back in original state
                    # and execute the steps via a normal rotate() call
                    self.parent.state = self.original_state[:]
                    self.parent.solution = self.original_solution[:]

                    for step in steps_to_hereA:
                        self.parent.rotate(step)

                    lt_state = self.state()

                    #log.info("%s: AStar found match %d steps in, %s, lt_state %s, AStar count %d, f_cost %d" %
                    #         (self, len(steps_to_hereA), ' '.join(steps_to_hereA), lt_state, astar_countA, f_costA))

                    if solutions_target is None:
                        return True
                    else:
                        cost_to_here = self.parent.get_solution_len_minus_rotates(steps_to_hereA)
                        cost_to_goal = self.parent.lt_tsai_phase2_centers.heuristic()
                        f_cost = cost_to_here + cost_to_goal
                        solutions.append((f_cost, cost_to_here, self.parent.solution[:]))

                        if len(solutions) >= solutions_target:
                            log.warning("reached solutions_target %d, we have %d" % (solutions_target, len(solutions)))
                            return solutions

            if astar_countA % 1000 == 0:
                log.info("%s: AStar countA %d, solutions %d, workqA depth %d, f_costA %d, steps_to_hereA %s" %
                    (self, astar_countA, len(solutions), len(workqA), f_costA, ' '.join(steps_to_hereA)))
                #log.info("%s: AStar countB %d, workqB depth %d, f_costB %d, steps_to_hereB %s\n" % (self, astar_countB, len(workqB), f_costB, ' '.join(steps_to_hereB)))

            # If we have already explored the exact same scenario down another branch
            # then we can stop looking down this branch
            if lt_stateA not in exploredA:
                #exploredA[lt_stateA] = steps_to_hereA[:]

                if steps_to_hereA:
                    prev_step = steps_to_hereA[-1]
                else:
                    prev_step = None

                # ==============
                # Keep Searching
                # ==============
                for step in self.moves_all:

                    #if steps_cancel_out(prev_step, step):
                    #    continue

                    if steps_on_same_face_and_layer(prev_step, step):
                        continue

                    self.parent.state = self.rotate_xxx(prev_stateA[:], step)

                    # calculate f_cost which is the cost to where we are plus the estimated cost to reach our goal
                    len_steps_to_hereA_plus_step = self.parent.get_solution_len_minus_rotates(steps_to_hereA) + 1
                    cost_to_here = len_steps_to_hereA_plus_step

                    cost_to_goal = self.ida_heuristic(use_lt_as_prune=False)
                    f_cost = cost_to_here + cost_to_goal

                    # The workq must remain sorted with lowest f_cost entries coming first, use
                    # cost_to_goal as a tie breaker
                    #steps_to_here_plus_step = tuple(list(steps_to_hereA[:]) + [step,])
                    steps_to_here_plus_step = steps_to_hereA[:] + [step,]

                    if max_depth is not None and len_steps_to_hereA_plus_step > max_depth:
                        continue

                    workq_tuple = (f_cost, len_steps_to_hereA_plus_step, cost_to_goal, steps_to_here_plus_step, self.parent.state[:])
                    insert_position = bisect.bisect_right(workqA, workq_tuple)
                    workqA.insert(insert_position, workq_tuple)

        if solutions:
            return solutions
        else:
            raise NoAStarSolution("%s FAILED" % self)

    def solve(self):
        start_time0 = dt.datetime.now()

        if self._solve():
            return True

        return self.astar_search()


class LookupTableIDA(LookupTableAStar):

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

        if self.search_complete(lt_state, steps_to_here):
            #log.info("%s: IDA found match %d steps in, %s, lt_state %s, f_cost %d (cost_to_here %d, cost_to_goal %d)" %
            #         (self, len(steps_to_here), ' '.join(steps_to_here), lt_state, f_cost, cost_to_here, cost_to_goal))
            log.info("%s: IDA found match %d steps in, f_cost %d (%d + %d)" %
                     (self, len(steps_to_here), f_cost, cost_to_here, cost_to_goal))
            return True

        # ==============
        # Keep Searching
        # ==============
        if f_cost > threshold:
            return False

        # If we have already explored the exact same scenario down another branch
        # then we can stop looking down this branch
        explored_cost_to_here = self.explored.get(lt_state)

        if explored_cost_to_here is not None and explored_cost_to_here <= cost_to_here:
            return False
        self.explored[lt_state] = cost_to_here

        for step in self.moves_all:

            #if steps_cancel_out(prev_step, step):
            #    continue

            if steps_on_same_face_and_layer(prev_step, step):
                continue

            self.parent.state = self.rotate_xxx(prev_state[:], step)

            if self.ida_search(steps_to_here + [step,], threshold, step, self.parent.state[:]):
                return True

        self.parent.state = prev_state[:]
        return False

    def solve(self, min_ida_threshold=None, max_ida_threshold=99):
        """
        The goal is to find a sequence of moves that will put the cube in a state that is
        in our lookup table
        """
        start_time0 = dt.datetime.now()

        if self._solve():
            return True

        if min_ida_threshold is None:
            min_ida_threshold = self.ida_heuristic()

        # If this is the case the range loop below isn't worth running
        if min_ida_threshold >= max_ida_threshold+1:
            raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))

        log.info("%s: IDA threshold range %d->%d" % (self, min_ida_threshold, max_ida_threshold))

        for threshold in range(min_ida_threshold, max_ida_threshold+1):
            steps_to_here = []
            start_time1 = dt.datetime.now()
            self.ida_count = 0
            self.explored = {}

            if self.ida_search(steps_to_here, threshold, None, self.original_state[:]):
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d branches, took %s (%s total)" %
                    (self, threshold, self.ida_count,
                     pretty_time(end_time1 - start_time1),
                     pretty_time(end_time1 - start_time0)))
                return True
            else:
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d branches, took %s" %
                    (self, threshold, self.ida_count, pretty_time(end_time1 - start_time1)))

        # The only time we will get here is when max_ida_threshold is a low number.  It will be up to the caller to:
        # - 'solve' one of their prune tables to put the cube in a state that we can find a solution for a little more easily
        # - call ida_solve() again but with a near infinite max_ida_threshold...99 is close enough to infinity for IDA purposes
        log.info("%s: could not find a solution via IDA with max threshold of %d " % (self, max_ida_threshold))

        self.parent.state = self.original_state[:]
        self.parent.solution = self.original_solution[:]

        raise NoIDASolution("%s FAILED with range %d->%d" % (self, min_ida_threshold, max_ida_threshold+1))

stage_first_four_edges_wing_str_combos = (
    ('BD', 'BL', 'BR', 'BU'),
    ('BD', 'BL', 'BR', 'DF'),
    ('BD', 'BL', 'BR', 'DL'),
    ('BD', 'BL', 'BR', 'DR'),
    ('BD', 'BL', 'BR', 'FL'),
    ('BD', 'BL', 'BR', 'FR'),
    ('BD', 'BL', 'BR', 'FU'),
    ('BD', 'BL', 'BR', 'LU'),
    ('BD', 'BL', 'BR', 'RU'),
    ('BD', 'BL', 'BU', 'DF'),
    ('BD', 'BL', 'BU', 'DL'),
    ('BD', 'BL', 'BU', 'DR'),
    ('BD', 'BL', 'BU', 'FL'),
    ('BD', 'BL', 'BU', 'FR'),
    ('BD', 'BL', 'BU', 'FU'),
    ('BD', 'BL', 'BU', 'LU'),
    ('BD', 'BL', 'BU', 'RU'),
    ('BD', 'BL', 'DF', 'DL'),
    ('BD', 'BL', 'DF', 'DR'),
    ('BD', 'BL', 'DF', 'FL'),
    ('BD', 'BL', 'DF', 'FR'),
    ('BD', 'BL', 'DF', 'FU'),
    ('BD', 'BL', 'DF', 'LU'),
    ('BD', 'BL', 'DF', 'RU'),
    ('BD', 'BL', 'DL', 'DR'),
    ('BD', 'BL', 'DL', 'FL'),
    ('BD', 'BL', 'DL', 'FR'),
    ('BD', 'BL', 'DL', 'FU'),
    ('BD', 'BL', 'DL', 'LU'),
    ('BD', 'BL', 'DL', 'RU'),
    ('BD', 'BL', 'DR', 'FL'),
    ('BD', 'BL', 'DR', 'FR'),
    ('BD', 'BL', 'DR', 'FU'),
    ('BD', 'BL', 'DR', 'LU'),
    ('BD', 'BL', 'DR', 'RU'),
    ('BD', 'BL', 'FL', 'FR'),
    ('BD', 'BL', 'FL', 'FU'),
    ('BD', 'BL', 'FL', 'LU'),
    ('BD', 'BL', 'FL', 'RU'),
    ('BD', 'BL', 'FR', 'FU'),
    ('BD', 'BL', 'FR', 'LU'),
    ('BD', 'BL', 'FR', 'RU'),
    ('BD', 'BL', 'FU', 'LU'),
    ('BD', 'BL', 'FU', 'RU'),
    ('BD', 'BL', 'LU', 'RU'),
    ('BD', 'BR', 'BU', 'DF'),
    ('BD', 'BR', 'BU', 'DL'),
    ('BD', 'BR', 'BU', 'DR'),
    ('BD', 'BR', 'BU', 'FL'),
    ('BD', 'BR', 'BU', 'FR'),
    ('BD', 'BR', 'BU', 'FU'),
    ('BD', 'BR', 'BU', 'LU'),
    ('BD', 'BR', 'BU', 'RU'),
    ('BD', 'BR', 'DF', 'DL'),
    ('BD', 'BR', 'DF', 'DR'),
    ('BD', 'BR', 'DF', 'FL'),
    ('BD', 'BR', 'DF', 'FR'),
    ('BD', 'BR', 'DF', 'FU'),
    ('BD', 'BR', 'DF', 'LU'),
    ('BD', 'BR', 'DF', 'RU'),
    ('BD', 'BR', 'DL', 'DR'),
    ('BD', 'BR', 'DL', 'FL'),
    ('BD', 'BR', 'DL', 'FR'),
    ('BD', 'BR', 'DL', 'FU'),
    ('BD', 'BR', 'DL', 'LU'),
    ('BD', 'BR', 'DL', 'RU'),
    ('BD', 'BR', 'DR', 'FL'),
    ('BD', 'BR', 'DR', 'FR'),
    ('BD', 'BR', 'DR', 'FU'),
    ('BD', 'BR', 'DR', 'LU'),
    ('BD', 'BR', 'DR', 'RU'),
    ('BD', 'BR', 'FL', 'FR'),
    ('BD', 'BR', 'FL', 'FU'),
    ('BD', 'BR', 'FL', 'LU'),
    ('BD', 'BR', 'FL', 'RU'),
    ('BD', 'BR', 'FR', 'FU'),
    ('BD', 'BR', 'FR', 'LU'),
    ('BD', 'BR', 'FR', 'RU'),
    ('BD', 'BR', 'FU', 'LU'),
    ('BD', 'BR', 'FU', 'RU'),
    ('BD', 'BR', 'LU', 'RU'),
    ('BD', 'BU', 'DF', 'DL'),
    ('BD', 'BU', 'DF', 'DR'),
    ('BD', 'BU', 'DF', 'FL'),
    ('BD', 'BU', 'DF', 'FR'),
    ('BD', 'BU', 'DF', 'FU'),
    ('BD', 'BU', 'DF', 'LU'),
    ('BD', 'BU', 'DF', 'RU'),
    ('BD', 'BU', 'DL', 'DR'),
    ('BD', 'BU', 'DL', 'FL'),
    ('BD', 'BU', 'DL', 'FR'),
    ('BD', 'BU', 'DL', 'FU'),
    ('BD', 'BU', 'DL', 'LU'),
    ('BD', 'BU', 'DL', 'RU'),
    ('BD', 'BU', 'DR', 'FL'),
    ('BD', 'BU', 'DR', 'FR'),
    ('BD', 'BU', 'DR', 'FU'),
    ('BD', 'BU', 'DR', 'LU'),
    ('BD', 'BU', 'DR', 'RU'),
    ('BD', 'BU', 'FL', 'FR'),
    ('BD', 'BU', 'FL', 'FU'),
    ('BD', 'BU', 'FL', 'LU'),
    ('BD', 'BU', 'FL', 'RU'),
    ('BD', 'BU', 'FR', 'FU'),
    ('BD', 'BU', 'FR', 'LU'),
    ('BD', 'BU', 'FR', 'RU'),
    ('BD', 'BU', 'FU', 'LU'),
    ('BD', 'BU', 'FU', 'RU'),
    ('BD', 'BU', 'LU', 'RU'),
    ('BD', 'DF', 'DL', 'DR'),
    ('BD', 'DF', 'DL', 'FL'),
    ('BD', 'DF', 'DL', 'FR'),
    ('BD', 'DF', 'DL', 'FU'),
    ('BD', 'DF', 'DL', 'LU'),
    ('BD', 'DF', 'DL', 'RU'),
    ('BD', 'DF', 'DR', 'FL'),
    ('BD', 'DF', 'DR', 'FR'),
    ('BD', 'DF', 'DR', 'FU'),
    ('BD', 'DF', 'DR', 'LU'),
    ('BD', 'DF', 'DR', 'RU'),
    ('BD', 'DF', 'FL', 'FR'),
    ('BD', 'DF', 'FL', 'FU'),
    ('BD', 'DF', 'FL', 'LU'),
    ('BD', 'DF', 'FL', 'RU'),
    ('BD', 'DF', 'FR', 'FU'),
    ('BD', 'DF', 'FR', 'LU'),
    ('BD', 'DF', 'FR', 'RU'),
    ('BD', 'DF', 'FU', 'LU'),
    ('BD', 'DF', 'FU', 'RU'),
    ('BD', 'DF', 'LU', 'RU'),
    ('BD', 'DL', 'DR', 'FL'),
    ('BD', 'DL', 'DR', 'FR'),
    ('BD', 'DL', 'DR', 'FU'),
    ('BD', 'DL', 'DR', 'LU'),
    ('BD', 'DL', 'DR', 'RU'),
    ('BD', 'DL', 'FL', 'FR'),
    ('BD', 'DL', 'FL', 'FU'),
    ('BD', 'DL', 'FL', 'LU'),
    ('BD', 'DL', 'FL', 'RU'),
    ('BD', 'DL', 'FR', 'FU'),
    ('BD', 'DL', 'FR', 'LU'),
    ('BD', 'DL', 'FR', 'RU'),
    ('BD', 'DL', 'FU', 'LU'),
    ('BD', 'DL', 'FU', 'RU'),
    ('BD', 'DL', 'LU', 'RU'),
    ('BD', 'DR', 'FL', 'FR'),
    ('BD', 'DR', 'FL', 'FU'),
    ('BD', 'DR', 'FL', 'LU'),
    ('BD', 'DR', 'FL', 'RU'),
    ('BD', 'DR', 'FR', 'FU'),
    ('BD', 'DR', 'FR', 'LU'),
    ('BD', 'DR', 'FR', 'RU'),
    ('BD', 'DR', 'FU', 'LU'),
    ('BD', 'DR', 'FU', 'RU'),
    ('BD', 'DR', 'LU', 'RU'),
    ('BD', 'FL', 'FR', 'FU'),
    ('BD', 'FL', 'FR', 'LU'),
    ('BD', 'FL', 'FR', 'RU'),
    ('BD', 'FL', 'FU', 'LU'),
    ('BD', 'FL', 'FU', 'RU'),
    ('BD', 'FL', 'LU', 'RU'),
    ('BD', 'FR', 'FU', 'LU'),
    ('BD', 'FR', 'FU', 'RU'),
    ('BD', 'FR', 'LU', 'RU'),
    ('BD', 'FU', 'LU', 'RU'),
    ('BL', 'BR', 'BU', 'DF'),
    ('BL', 'BR', 'BU', 'DL'),
    ('BL', 'BR', 'BU', 'DR'),
    ('BL', 'BR', 'BU', 'FL'),
    ('BL', 'BR', 'BU', 'FR'),
    ('BL', 'BR', 'BU', 'FU'),
    ('BL', 'BR', 'BU', 'LU'),
    ('BL', 'BR', 'BU', 'RU'),
    ('BL', 'BR', 'DF', 'DL'),
    ('BL', 'BR', 'DF', 'DR'),
    ('BL', 'BR', 'DF', 'FL'),
    ('BL', 'BR', 'DF', 'FR'),
    ('BL', 'BR', 'DF', 'FU'),
    ('BL', 'BR', 'DF', 'LU'),
    ('BL', 'BR', 'DF', 'RU'),
    ('BL', 'BR', 'DL', 'DR'),
    ('BL', 'BR', 'DL', 'FL'),
    ('BL', 'BR', 'DL', 'FR'),
    ('BL', 'BR', 'DL', 'FU'),
    ('BL', 'BR', 'DL', 'LU'),
    ('BL', 'BR', 'DL', 'RU'),
    ('BL', 'BR', 'DR', 'FL'),
    ('BL', 'BR', 'DR', 'FR'),
    ('BL', 'BR', 'DR', 'FU'),
    ('BL', 'BR', 'DR', 'LU'),
    ('BL', 'BR', 'DR', 'RU'),
    ('BL', 'BR', 'FL', 'FR'),
    ('BL', 'BR', 'FL', 'FU'),
    ('BL', 'BR', 'FL', 'LU'),
    ('BL', 'BR', 'FL', 'RU'),
    ('BL', 'BR', 'FR', 'FU'),
    ('BL', 'BR', 'FR', 'LU'),
    ('BL', 'BR', 'FR', 'RU'),
    ('BL', 'BR', 'FU', 'LU'),
    ('BL', 'BR', 'FU', 'RU'),
    ('BL', 'BR', 'LU', 'RU'),
    ('BL', 'BU', 'DF', 'DL'),
    ('BL', 'BU', 'DF', 'DR'),
    ('BL', 'BU', 'DF', 'FL'),
    ('BL', 'BU', 'DF', 'FR'),
    ('BL', 'BU', 'DF', 'FU'),
    ('BL', 'BU', 'DF', 'LU'),
    ('BL', 'BU', 'DF', 'RU'),
    ('BL', 'BU', 'DL', 'DR'),
    ('BL', 'BU', 'DL', 'FL'),
    ('BL', 'BU', 'DL', 'FR'),
    ('BL', 'BU', 'DL', 'FU'),
    ('BL', 'BU', 'DL', 'LU'),
    ('BL', 'BU', 'DL', 'RU'),
    ('BL', 'BU', 'DR', 'FL'),
    ('BL', 'BU', 'DR', 'FR'),
    ('BL', 'BU', 'DR', 'FU'),
    ('BL', 'BU', 'DR', 'LU'),
    ('BL', 'BU', 'DR', 'RU'),
    ('BL', 'BU', 'FL', 'FR'),
    ('BL', 'BU', 'FL', 'FU'),
    ('BL', 'BU', 'FL', 'LU'),
    ('BL', 'BU', 'FL', 'RU'),
    ('BL', 'BU', 'FR', 'FU'),
    ('BL', 'BU', 'FR', 'LU'),
    ('BL', 'BU', 'FR', 'RU'),
    ('BL', 'BU', 'FU', 'LU'),
    ('BL', 'BU', 'FU', 'RU'),
    ('BL', 'BU', 'LU', 'RU'),
    ('BL', 'DF', 'DL', 'DR'),
    ('BL', 'DF', 'DL', 'FL'),
    ('BL', 'DF', 'DL', 'FR'),
    ('BL', 'DF', 'DL', 'FU'),
    ('BL', 'DF', 'DL', 'LU'),
    ('BL', 'DF', 'DL', 'RU'),
    ('BL', 'DF', 'DR', 'FL'),
    ('BL', 'DF', 'DR', 'FR'),
    ('BL', 'DF', 'DR', 'FU'),
    ('BL', 'DF', 'DR', 'LU'),
    ('BL', 'DF', 'DR', 'RU'),
    ('BL', 'DF', 'FL', 'FR'),
    ('BL', 'DF', 'FL', 'FU'),
    ('BL', 'DF', 'FL', 'LU'),
    ('BL', 'DF', 'FL', 'RU'),
    ('BL', 'DF', 'FR', 'FU'),
    ('BL', 'DF', 'FR', 'LU'),
    ('BL', 'DF', 'FR', 'RU'),
    ('BL', 'DF', 'FU', 'LU'),
    ('BL', 'DF', 'FU', 'RU'),
    ('BL', 'DF', 'LU', 'RU'),
    ('BL', 'DL', 'DR', 'FL'),
    ('BL', 'DL', 'DR', 'FR'),
    ('BL', 'DL', 'DR', 'FU'),
    ('BL', 'DL', 'DR', 'LU'),
    ('BL', 'DL', 'DR', 'RU'),
    ('BL', 'DL', 'FL', 'FR'),
    ('BL', 'DL', 'FL', 'FU'),
    ('BL', 'DL', 'FL', 'LU'),
    ('BL', 'DL', 'FL', 'RU'),
    ('BL', 'DL', 'FR', 'FU'),
    ('BL', 'DL', 'FR', 'LU'),
    ('BL', 'DL', 'FR', 'RU'),
    ('BL', 'DL', 'FU', 'LU'),
    ('BL', 'DL', 'FU', 'RU'),
    ('BL', 'DL', 'LU', 'RU'),
    ('BL', 'DR', 'FL', 'FR'),
    ('BL', 'DR', 'FL', 'FU'),
    ('BL', 'DR', 'FL', 'LU'),
    ('BL', 'DR', 'FL', 'RU'),
    ('BL', 'DR', 'FR', 'FU'),
    ('BL', 'DR', 'FR', 'LU'),
    ('BL', 'DR', 'FR', 'RU'),
    ('BL', 'DR', 'FU', 'LU'),
    ('BL', 'DR', 'FU', 'RU'),
    ('BL', 'DR', 'LU', 'RU'),
    ('BL', 'FL', 'FR', 'FU'),
    ('BL', 'FL', 'FR', 'LU'),
    ('BL', 'FL', 'FR', 'RU'),
    ('BL', 'FL', 'FU', 'LU'),
    ('BL', 'FL', 'FU', 'RU'),
    ('BL', 'FL', 'LU', 'RU'),
    ('BL', 'FR', 'FU', 'LU'),
    ('BL', 'FR', 'FU', 'RU'),
    ('BL', 'FR', 'LU', 'RU'),
    ('BL', 'FU', 'LU', 'RU'),
    ('BR', 'BU', 'DF', 'DL'),
    ('BR', 'BU', 'DF', 'DR'),
    ('BR', 'BU', 'DF', 'FL'),
    ('BR', 'BU', 'DF', 'FR'),
    ('BR', 'BU', 'DF', 'FU'),
    ('BR', 'BU', 'DF', 'LU'),
    ('BR', 'BU', 'DF', 'RU'),
    ('BR', 'BU', 'DL', 'DR'),
    ('BR', 'BU', 'DL', 'FL'),
    ('BR', 'BU', 'DL', 'FR'),
    ('BR', 'BU', 'DL', 'FU'),
    ('BR', 'BU', 'DL', 'LU'),
    ('BR', 'BU', 'DL', 'RU'),
    ('BR', 'BU', 'DR', 'FL'),
    ('BR', 'BU', 'DR', 'FR'),
    ('BR', 'BU', 'DR', 'FU'),
    ('BR', 'BU', 'DR', 'LU'),
    ('BR', 'BU', 'DR', 'RU'),
    ('BR', 'BU', 'FL', 'FR'),
    ('BR', 'BU', 'FL', 'FU'),
    ('BR', 'BU', 'FL', 'LU'),
    ('BR', 'BU', 'FL', 'RU'),
    ('BR', 'BU', 'FR', 'FU'),
    ('BR', 'BU', 'FR', 'LU'),
    ('BR', 'BU', 'FR', 'RU'),
    ('BR', 'BU', 'FU', 'LU'),
    ('BR', 'BU', 'FU', 'RU'),
    ('BR', 'BU', 'LU', 'RU'),
    ('BR', 'DF', 'DL', 'DR'),
    ('BR', 'DF', 'DL', 'FL'),
    ('BR', 'DF', 'DL', 'FR'),
    ('BR', 'DF', 'DL', 'FU'),
    ('BR', 'DF', 'DL', 'LU'),
    ('BR', 'DF', 'DL', 'RU'),
    ('BR', 'DF', 'DR', 'FL'),
    ('BR', 'DF', 'DR', 'FR'),
    ('BR', 'DF', 'DR', 'FU'),
    ('BR', 'DF', 'DR', 'LU'),
    ('BR', 'DF', 'DR', 'RU'),
    ('BR', 'DF', 'FL', 'FR'),
    ('BR', 'DF', 'FL', 'FU'),
    ('BR', 'DF', 'FL', 'LU'),
    ('BR', 'DF', 'FL', 'RU'),
    ('BR', 'DF', 'FR', 'FU'),
    ('BR', 'DF', 'FR', 'LU'),
    ('BR', 'DF', 'FR', 'RU'),
    ('BR', 'DF', 'FU', 'LU'),
    ('BR', 'DF', 'FU', 'RU'),
    ('BR', 'DF', 'LU', 'RU'),
    ('BR', 'DL', 'DR', 'FL'),
    ('BR', 'DL', 'DR', 'FR'),
    ('BR', 'DL', 'DR', 'FU'),
    ('BR', 'DL', 'DR', 'LU'),
    ('BR', 'DL', 'DR', 'RU'),
    ('BR', 'DL', 'FL', 'FR'),
    ('BR', 'DL', 'FL', 'FU'),
    ('BR', 'DL', 'FL', 'LU'),
    ('BR', 'DL', 'FL', 'RU'),
    ('BR', 'DL', 'FR', 'FU'),
    ('BR', 'DL', 'FR', 'LU'),
    ('BR', 'DL', 'FR', 'RU'),
    ('BR', 'DL', 'FU', 'LU'),
    ('BR', 'DL', 'FU', 'RU'),
    ('BR', 'DL', 'LU', 'RU'),
    ('BR', 'DR', 'FL', 'FR'),
    ('BR', 'DR', 'FL', 'FU'),
    ('BR', 'DR', 'FL', 'LU'),
    ('BR', 'DR', 'FL', 'RU'),
    ('BR', 'DR', 'FR', 'FU'),
    ('BR', 'DR', 'FR', 'LU'),
    ('BR', 'DR', 'FR', 'RU'),
    ('BR', 'DR', 'FU', 'LU'),
    ('BR', 'DR', 'FU', 'RU'),
    ('BR', 'DR', 'LU', 'RU'),
    ('BR', 'FL', 'FR', 'FU'),
    ('BR', 'FL', 'FR', 'LU'),
    ('BR', 'FL', 'FR', 'RU'),
    ('BR', 'FL', 'FU', 'LU'),
    ('BR', 'FL', 'FU', 'RU'),
    ('BR', 'FL', 'LU', 'RU'),
    ('BR', 'FR', 'FU', 'LU'),
    ('BR', 'FR', 'FU', 'RU'),
    ('BR', 'FR', 'LU', 'RU'),
    ('BR', 'FU', 'LU', 'RU'),
    ('BU', 'DF', 'DL', 'DR'),
    ('BU', 'DF', 'DL', 'FL'),
    ('BU', 'DF', 'DL', 'FR'),
    ('BU', 'DF', 'DL', 'FU'),
    ('BU', 'DF', 'DL', 'LU'),
    ('BU', 'DF', 'DL', 'RU'),
    ('BU', 'DF', 'DR', 'FL'),
    ('BU', 'DF', 'DR', 'FR'),
    ('BU', 'DF', 'DR', 'FU'),
    ('BU', 'DF', 'DR', 'LU'),
    ('BU', 'DF', 'DR', 'RU'),
    ('BU', 'DF', 'FL', 'FR'),
    ('BU', 'DF', 'FL', 'FU'),
    ('BU', 'DF', 'FL', 'LU'),
    ('BU', 'DF', 'FL', 'RU'),
    ('BU', 'DF', 'FR', 'FU'),
    ('BU', 'DF', 'FR', 'LU'),
    ('BU', 'DF', 'FR', 'RU'),
    ('BU', 'DF', 'FU', 'LU'),
    ('BU', 'DF', 'FU', 'RU'),
    ('BU', 'DF', 'LU', 'RU'),
    ('BU', 'DL', 'DR', 'FL'),
    ('BU', 'DL', 'DR', 'FR'),
    ('BU', 'DL', 'DR', 'FU'),
    ('BU', 'DL', 'DR', 'LU'),
    ('BU', 'DL', 'DR', 'RU'),
    ('BU', 'DL', 'FL', 'FR'),
    ('BU', 'DL', 'FL', 'FU'),
    ('BU', 'DL', 'FL', 'LU'),
    ('BU', 'DL', 'FL', 'RU'),
    ('BU', 'DL', 'FR', 'FU'),
    ('BU', 'DL', 'FR', 'LU'),
    ('BU', 'DL', 'FR', 'RU'),
    ('BU', 'DL', 'FU', 'LU'),
    ('BU', 'DL', 'FU', 'RU'),
    ('BU', 'DL', 'LU', 'RU'),
    ('BU', 'DR', 'FL', 'FR'),
    ('BU', 'DR', 'FL', 'FU'),
    ('BU', 'DR', 'FL', 'LU'),
    ('BU', 'DR', 'FL', 'RU'),
    ('BU', 'DR', 'FR', 'FU'),
    ('BU', 'DR', 'FR', 'LU'),
    ('BU', 'DR', 'FR', 'RU'),
    ('BU', 'DR', 'FU', 'LU'),
    ('BU', 'DR', 'FU', 'RU'),
    ('BU', 'DR', 'LU', 'RU'),
    ('BU', 'FL', 'FR', 'FU'),
    ('BU', 'FL', 'FR', 'LU'),
    ('BU', 'FL', 'FR', 'RU'),
    ('BU', 'FL', 'FU', 'LU'),
    ('BU', 'FL', 'FU', 'RU'),
    ('BU', 'FL', 'LU', 'RU'),
    ('BU', 'FR', 'FU', 'LU'),
    ('BU', 'FR', 'FU', 'RU'),
    ('BU', 'FR', 'LU', 'RU'),
    ('BU', 'FU', 'LU', 'RU'),
    ('DF', 'DL', 'DR', 'FL'),
    ('DF', 'DL', 'DR', 'FR'),
    ('DF', 'DL', 'DR', 'FU'),
    ('DF', 'DL', 'DR', 'LU'),
    ('DF', 'DL', 'DR', 'RU'),
    ('DF', 'DL', 'FL', 'FR'),
    ('DF', 'DL', 'FL', 'FU'),
    ('DF', 'DL', 'FL', 'LU'),
    ('DF', 'DL', 'FL', 'RU'),
    ('DF', 'DL', 'FR', 'FU'),
    ('DF', 'DL', 'FR', 'LU'),
    ('DF', 'DL', 'FR', 'RU'),
    ('DF', 'DL', 'FU', 'LU'),
    ('DF', 'DL', 'FU', 'RU'),
    ('DF', 'DL', 'LU', 'RU'),
    ('DF', 'DR', 'FL', 'FR'),
    ('DF', 'DR', 'FL', 'FU'),
    ('DF', 'DR', 'FL', 'LU'),
    ('DF', 'DR', 'FL', 'RU'),
    ('DF', 'DR', 'FR', 'FU'),
    ('DF', 'DR', 'FR', 'LU'),
    ('DF', 'DR', 'FR', 'RU'),
    ('DF', 'DR', 'FU', 'LU'),
    ('DF', 'DR', 'FU', 'RU'),
    ('DF', 'DR', 'LU', 'RU'),
    ('DF', 'FL', 'FR', 'FU'),
    ('DF', 'FL', 'FR', 'LU'),
    ('DF', 'FL', 'FR', 'RU'),
    ('DF', 'FL', 'FU', 'LU'),
    ('DF', 'FL', 'FU', 'RU'),
    ('DF', 'FL', 'LU', 'RU'),
    ('DF', 'FR', 'FU', 'LU'),
    ('DF', 'FR', 'FU', 'RU'),
    ('DF', 'FR', 'LU', 'RU'),
    ('DF', 'FU', 'LU', 'RU'),
    ('DL', 'DR', 'FL', 'FR'),
    ('DL', 'DR', 'FL', 'FU'),
    ('DL', 'DR', 'FL', 'LU'),
    ('DL', 'DR', 'FL', 'RU'),
    ('DL', 'DR', 'FR', 'FU'),
    ('DL', 'DR', 'FR', 'LU'),
    ('DL', 'DR', 'FR', 'RU'),
    ('DL', 'DR', 'FU', 'LU'),
    ('DL', 'DR', 'FU', 'RU'),
    ('DL', 'DR', 'LU', 'RU'),
    ('DL', 'FL', 'FR', 'FU'),
    ('DL', 'FL', 'FR', 'LU'),
    ('DL', 'FL', 'FR', 'RU'),
    ('DL', 'FL', 'FU', 'LU'),
    ('DL', 'FL', 'FU', 'RU'),
    ('DL', 'FL', 'LU', 'RU'),
    ('DL', 'FR', 'FU', 'LU'),
    ('DL', 'FR', 'FU', 'RU'),
    ('DL', 'FR', 'LU', 'RU'),
    ('DL', 'FU', 'LU', 'RU'),
    ('DR', 'FL', 'FR', 'FU'),
    ('DR', 'FL', 'FR', 'LU'),
    ('DR', 'FL', 'FR', 'RU'),
    ('DR', 'FL', 'FU', 'LU'),
    ('DR', 'FL', 'FU', 'RU'),
    ('DR', 'FL', 'LU', 'RU'),
    ('DR', 'FR', 'FU', 'LU'),
    ('DR', 'FR', 'FU', 'RU'),
    ('DR', 'FR', 'LU', 'RU'),
    ('DR', 'FU', 'LU', 'RU'),
    ('FL', 'FR', 'FU', 'LU'),
    ('FL', 'FR', 'FU', 'RU'),
    ('FL', 'FR', 'LU', 'RU'),
    ('FL', 'FU', 'LU', 'RU'),
    ('FR', 'FU', 'LU', 'RU'),
)


if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
