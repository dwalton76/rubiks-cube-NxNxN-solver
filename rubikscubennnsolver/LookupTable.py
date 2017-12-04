
import datetime as dt
from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.rotate_xxx import rotate_222, rotate_444, rotate_555, rotate_666, rotate_777
from subprocess import check_output
import json
import logging
import math
import os
import shutil
import subprocess
import sys


log = logging.getLogger(__name__)

# NOTE: always use list slicing instead of copy for lists
# See the 3rd post here:
# https://stackoverflow.com/questions/2612802/how-to-clone-or-copy-a-list
# For 100k list copy.copy() took 1.488s where slicing took 0.039s...that is a 38x improvement

class ImplementThis(Exception):
    pass


class NoSteps(Exception):
    pass


class NoIDASolution(Exception):
    pass


def get_first_last_for_binary_search(line_number_to_state, state_to_find, linecount):
    first = 0
    last = linecount - 1
    to_delete = []

    for linenumber in sorted(line_number_to_state.keys()):
        state = line_number_to_state[linenumber]

        if state < state_to_find:
            first = linenumber
            to_delete.append(linenumber)

        elif state == state_to_find:
            first = linenumber
            last = linenumber
            break

        elif state > state_to_find:
            last = linenumber
            break

    for linenumber in to_delete:
        del line_number_to_state[linenumber]

    return (line_number_to_state, first, last)


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

        assert self.filename.startswith('lookup-table'), "We only support lookup-table*.txt files"
        assert self.filename.endswith('.txt'), "We only support lookup-table*.txt files"

        if 'dummy' not in self.filename:
            assert self.linecount, "%s linecount is %s" % (self, self.linecount)

        if not os.path.exists(self.filename):
            if not os.path.exists(self.filename_gz):

                # Special cases where I could not get them one under 100M so I split it via:
                # split -b 40m lookup-table-4x4x4-step70-tsai-phase3.txt.gz "lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-"
                if self.filename_gz == 'lookup-table-4x4x4-step70-tsai-phase3.txt.gz':

                    # Download part-aa
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-aa" %\
                        (self.parent.size, self.parent.size, self.parent.size)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

                    # Download part-ab
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ab" %\
                        (self.parent.size, self.parent.size, self.parent.size)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

                    # Download part-ac
                    url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ac" %\
                        (self.parent.size, self.parent.size, self.parent.size)
                    log.info("Downloading table via 'wget %s'" % url)
                    subprocess.call(['wget', url])

                    subprocess.call('cat lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-* > lookup-table-4x4x4-step70-tsai-phase3.txt.gz', shell=True)
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-aa')
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ab')
                    os.unlink('lookup-table-4x4x4-step70-tsai-phase3.txt.gz.part-ac')

                elif self.filename_gz == 'lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz':

                    # Download all three parts
                    for extension in ('aa', 'ab', 'ac'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    subprocess.call('cat lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-* > lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz', shell=True)
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-aa')
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-ab')
                    os.unlink('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.gz.part-ac')

                elif self.filename_gz == 'lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz':

                    # Download all three parts
                    for extension in ('aa', 'ab', 'ac'):
                        url = "https://github.com/dwalton76/rubiks-cube-lookup-tables-%sx%sx%s/raw/master/lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-%s" %\
                            (self.parent.size, self.parent.size, self.parent.size, extension)
                        log.info("Downloading table via 'wget %s'" % url)
                        subprocess.call(['wget', url])

                    subprocess.call('cat lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-* > lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz', shell=True)
                    os.unlink('lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-aa')
                    os.unlink('lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-ab')
                    os.unlink('lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.txt.gz.part-ac')

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
        self.preloaded_cache = False

        # 'rb' mode is about 3x faster than 'r' mode
        self.fh_txt = open(self.filename, mode='rb')

    def __str__(self):
        return self.desc

    def preload_cache(self):
        log.info("%s: start preload_cache()" % self)
        self.fh_txt.seek(0)

        for line in self.fh_txt.readlines():
            (state, steps) = line.split(':')
            self.cache[state] = steps.split()
        self.fh_txt.seek(0)
        log.info("%s: end preload_cache()" % self)
        self.preloaded_cache = True

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

    def steps_for_list_of_states(self, list_of_states):
        list_of_states = sorted(list_of_states)
        results = []
        line_number_to_state = {}

        for state_to_find in list_of_states:
            (line_number_to_state, first, last) = get_first_last_for_binary_search(line_number_to_state, state_to_find, self.linecount)
            #log.info("%s: first %d, last %d, state_to_find %s" % (self, first, last, state_to_find))

            while first <= last:
                midpoint = int((first + last)/2)
                self.fh_txt.seek(midpoint * self.width)
                line = self.fh_txt.readline().rstrip()
                #log.info("%s: first %d, last %d, midpoint %d, width %d, state_to_find %s, line %s" % (self, first, last, midpoint, self.width, state_to_find, line))

                try:
                    (state, steps) = line.split(':')
                except Exception:
                    log.warning("%s: midpoint %d, width %d, state_to_find %s, line %s" % (self, midpoint, self.width, state_to_find, line))
                    raise

                line_number_to_state[midpoint] = state

                if state == state_to_find:
                    results.append((state_to_find, steps.split()))
                    break
                else:

                    if state_to_find < state:
                        last = midpoint-1
                    else:
                        first = midpoint+1

        return results

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
                #log.info("%s: solve() state %s found %s" % (self, state, ' '.join(steps)))

                for step in steps:
                    self.parent.rotate(step)
            else:
                self.parent.print_cube()
                raise NoSteps("%s: state %s does not have steps" % (self, state))


class LookupTableIDA(LookupTable):

    def __init__(self, parent, filename, state_target, moves_all, moves_illegal, prune_tables, linecount):
        LookupTable.__init__(self, parent, filename, state_target, linecount)
        self.prune_tables = prune_tables

        for x in moves_illegal:
            if x not in moves_all:
                raise Exception("illegal move %s is not in the list of legal moves" % x)

        self.moves_all = []
        for x in moves_all:
            if x not in moves_illegal:
                self.moves_all.append(x)

    def ida_heuristic_all_costs(self):
        """
        No longer used...save for rainy day
        """
        results = {}

        for pt in self.prune_tables:
            pt_state = pt.state()
            pt_steps = pt.steps(pt_state)

            if pt_state in pt.state_target:
                len_pt_steps = 0

            elif pt_steps:
                len_pt_steps = len(pt_steps)

                # There are few prune tables that I built where instead of listing the steps
                # for a state I just listed how many steps there would be.  I did this to save
                # space.  lookup-table-5x5x5-step13-UD-centers-stage-UFDB-only.txt is one such table.
                if len_pt_steps == 1 and pt_steps[0].isdigit():
                    len_pt_steps = int(pt_steps[0])

            elif pt.max_depth:
                # This is the exception to the rule but some prune tables such
                # as lookup-table-6x6x6-step23-UD-oblique-edge-pairing-LFRB-only.txt
                # are partial tables so use the max_depth of the table +1
                len_pt_steps = pt.max_depth + 1

            else:
                raise SolveError("%s does not have max_depth and does not have steps for %s, state_width %d" % (pt, pt_state, pt.state_width))

            results[pt.filename] = len_pt_steps

        return results

    def ida_heuristic(self, debug=False):
        cost_to_goal = 0
        pt_costs = []

        for pt in self.prune_tables:
            pt_state = pt.state()
            pt_steps = pt.steps(pt_state)

            if pt_state in pt.state_target:
                len_pt_steps = 0

                #if debug:
                #    log.info("%s: pt_state %s, cost 0, at target" % (pt, pt_state))

            elif pt_steps:
                len_pt_steps = len(pt_steps)

                # There are few prune tables that I built where instead of listing the steps
                # for a state I just listed how many steps there would be.  I did this to save
                # space.  lookup-table-5x5x5-step13-UD-centers-stage-UFDB-only.txt is one such table.
                if len_pt_steps == 1 and pt_steps[0].isdigit():
                    len_pt_steps = int(pt_steps[0])

                #if debug:
                #    log.info("%s: pt_state %s, cost %d" % (pt, pt_state, len_pt_steps))

            elif pt.max_depth:
                # This is the exception to the rule but some prune tables such
                # as lookup-table-6x6x6-step23-UD-oblique-edge-pairing-LFRB-only.txt
                # are partial tables so use the max_depth of the table +1
                len_pt_steps = pt.max_depth + 1

                #if debug:
                #    log.info("%s: pt_state %s, cost %d (max depth)" % (pt, pt_state, len_pt_steps))

            else:
                self.parent.print_cube()
                raise SolveError("%s does not have max_depth and does not have steps for %s, state_width %d" % (pt, pt_state, pt.state_width))

            if len_pt_steps > cost_to_goal:
                cost_to_goal = len_pt_steps

        #if debug:
        #    log.info("%s: cost_to_goal %d\n" % (self, cost_to_goal))

        return cost_to_goal

    def steps(self, state_to_find):
        """
        Return a list of the steps found in the lookup table for the current cube state
        This is very similar to LookupTable.steps(), the main difference is we do not
        populate self.cache with misses.
        """

        if self.preloaded_cache:
            return self.cache.get(state_to_find)
        else:
            line = self.binary_search(state_to_find)

            if line:
                (state, steps) = line.strip().split(':')
                return steps.split()

            return None

    def ida_search_complete(self, state, steps_to_here):
        steps = self.steps(state)

        if not steps:
            return False

        # =================================================
        # If there are steps for a state that means our IDA
        # search is done...woohoo!!
        # =================================================
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

    def ida_search(self, steps_to_here, threshold, prev_step, prev_state):
        """
        https://algorithmsinsight.wordpress.com/graph-theory-2/ida-star-algorithm-in-general/
        """
        self.ida_count += 1

        # calculate f_cost which is the cost to where we are plus the estimated cost to reach our goal
        cost_to_here = len(steps_to_here)
        cost_to_goal = self.ida_heuristic()
        f_cost = cost_to_here + cost_to_goal

        state = self.state()

        if self.ida_search_complete(state, steps_to_here):
            log.info("%s: IDA found match %d steps in, %s, state %s, f_cost %d (cost_to_here %d, cost_to_goal %d)" %
                     (self, len(steps_to_here), ' '.join(steps_to_here), state, f_cost, cost_to_here, cost_to_goal))
            return True

        # ==============
        # Keep Searching
        # ==============
        if f_cost > threshold:
            return False

        # If we have already explored the exact same scenario down another branch
        # then we can stop looking down this branch
        if (cost_to_here, state) in self.explored:
            return False
        self.explored.add((cost_to_here, state))

        for step in self.moves_all:

            # If this step cancels out the previous step then don't bother with this branch
            if prev_step is not None:

                # U2 followed by U2 is a no-op
                if step == prev_step and step.endswith("2"):
                    continue

                # U' followed by U is a no-op
                if step == prev_step[0:-1] and prev_step.endswith("'") and not step.endswith("'"):
                    continue

                # U followed by U' is a no-op
                if step[0:-1] == prev_step and not prev_step.endswith("'") and step.endswith("'"):
                    continue

            self.parent.state = self.rotate_xxx(prev_state[:], step)

            if self.ida_search(steps_to_here + [step,], threshold, step, self.parent.state[:]):
                return True

        self.parent.state = prev_state[:]
        return False

    def solve(self, min_ida_threshold=None, max_ida_threshold=99):
        """
        The goal is to find a sequence of moves that will put the cube in a state that is
        in our lookup table self.filename
        """
        start_time0 = dt.datetime.now()

        # This shouldn't happen since the lookup tables are in the repo
        if not self.filename_exists:
            raise SolveError("%s does not exist" % self.filename)

        state = self.state()
        #log.info("%s: ida_stage() state %s vs state_target %s" % (self, state, self.state_target))

        # The cube is already in the desired state, nothing to do
        if state in self.state_target:
            log.info("%s: IDA, cube is already at the target state %s" % (self, state))
            return

        # The cube is already in a state that is in our lookup table, nothing for IDA to do
        steps = self.steps(state)

        if steps:
            log.info("%s: IDA, cube is already in a state %s that is in our lookup table" % (self, state))

            # The cube is now in a state where it is in the lookup table, we may need
            # to do several lookups to get to our target state though. Use
            # LookupTabele's solve() to take us the rest of the way to the target state.
            LookupTable.solve(self)
            return

        # If we are here (odds are very high we will be) it means that the current
        # cube state was not in the lookup table.  We must now perform an IDA search
        # until we find a sequence of moves that takes us to a state that IS in the
        # lookup table.

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
            self.explored = set()

            if self.ida_search(steps_to_here, threshold, None, self.original_state[:]):
                end_time1 = dt.datetime.now()
                log.info("%s: IDA threshold %d, explored %d branches, took %s (%s total)" %
                    (self, threshold, self.ida_count,
                     pretty_time(end_time1 - start_time1),
                     pretty_time(end_time1 - start_time0)))
                return
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
