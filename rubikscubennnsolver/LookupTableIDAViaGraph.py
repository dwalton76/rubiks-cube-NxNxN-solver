# standard libraries
import logging
import os
import random
import re
import string
import subprocess
from typing import List

# rubiks cube libraries
from rubikscubennnsolver import reverse_steps
from rubikscubennnsolver.LookupTable import LookupTable, NoIDASolution, download_file_if_needed

logger = logging.getLogger(__name__)


def remove_failed_ida_output(lines: List[str]) -> List[str]:
    """
    Args:
        lines: log output from IDA

    Returns:
        the log output but with failed IDA output removed
    """
    result = []
    ida_output = []

    for line in lines:
        if line:
            ida_output.append(line)
        else:
            ida_output.append(line)

            if "IDA failed with range" not in "".join(ida_output):
                result.extend(ida_output)

            ida_output = []

    if ida_output and "IDA failed with range" not in "".join(ida_output):
        result.extend(ida_output)
        ida_output = []

    return result


class LookupTableIDAViaGraph(LookupTable):
    """
    multipliers
        1.04 will round 13 to 14, 14 to 15, etc
        1.05 will round 10 to 11, etc
        1.06 will round 9 to 10, etc
        1.07 will round 8 to 9, etc
        1.08 will round 7 to 8, etc
        1.09 will round 6 to 7, etc
        1.10 will round 5 to 6, etc
        1.11 will round 5 to 6, etc
        1.12 will round 5 to 6, etc
        1.13 will round 4 to 5, etc
    """

    def __init__(
        self,
        parent,
        filename: str = None,
        all_moves: List[str] = [],
        illegal_moves: List[str] = [],
        state_target: str = None,
        linecount: int = None,
        max_depth: int = None,
        filesize: int = None,
        legal_moves: List[str] = [],
        prune_tables=[],
        multiplier: float = None,
        main_table_state_length: int = None,
        main_table_max_depth: int = None,
        main_table_prune_tables=None,
        perfect_hash01_filename: str = None,
        perfect_hash02_filename: str = None,
        perfect_hash12_filename: str = None,
        perfect_hash34_filename: str = None,
        pt1_state_max: int = None,
        pt2_state_max: int = None,
        pt4_state_max: int = None,
        centers_only: bool = False,
        use_uthash: bool = False,
        C_ida_type: str = None,
    ):
        LookupTable.__init__(self, parent, filename, state_target, linecount, max_depth, filesize)
        self.recolor_positions = []
        self.recolor_map = {}
        self.nuke_corners = False
        self.nuke_edges = False
        self.nuke_centers = False
        self.prune_tables = prune_tables
        self.multiplier = multiplier
        self.main_table_state_length = main_table_state_length
        self.main_table_max_depth = main_table_max_depth
        self.main_table_prune_tables = main_table_prune_tables
        self.centers_only = centers_only
        self.use_uthash = use_uthash
        self.C_ida_type = C_ida_type

        if perfect_hash01_filename:
            self.perfect_hash01_filename = "lookup-tables/" + perfect_hash01_filename
        else:
            self.perfect_hash01_filename = perfect_hash01_filename

        if perfect_hash02_filename:
            self.perfect_hash02_filename = "lookup-tables/" + perfect_hash02_filename
        else:
            self.perfect_hash02_filename = perfect_hash02_filename

        if perfect_hash12_filename:
            self.perfect_hash12_filename = "lookup-tables/" + perfect_hash12_filename
        else:
            self.perfect_hash12_filename = perfect_hash12_filename

        if perfect_hash34_filename:
            self.perfect_hash34_filename = "lookup-tables/" + perfect_hash34_filename
        else:
            self.perfect_hash34_filename = perfect_hash34_filename

        self.pt1_state_max = pt1_state_max
        self.pt2_state_max = pt2_state_max
        self.pt4_state_max = pt4_state_max

        if self.perfect_hash01_filename:
            assert (
                self.perfect_hash01_filename and self.pt1_state_max
            ), "both perfect_hash01_filename and pt1_state_max must be specified"
            download_file_if_needed(self.perfect_hash01_filename)

        if self.perfect_hash02_filename:
            assert (
                self.perfect_hash02_filename and self.pt2_state_max
            ), "both perfect_hash02_filename and pt2_state_max must be specified"
            download_file_if_needed(self.perfect_hash02_filename)

        if self.perfect_hash12_filename:
            assert (
                self.perfect_hash12_filename and self.pt2_state_max
            ), "both perfect_hash12_filename and pt2_state_max must be specified"
            download_file_if_needed(self.perfect_hash12_filename)

        if self.perfect_hash34_filename:
            assert (
                self.perfect_hash34_filename and self.pt4_state_max
            ), "both perfect_hash34_filename and pt4_state_max must be specified"
            download_file_if_needed(self.perfect_hash34_filename)

        if legal_moves:
            self.all_moves = list(legal_moves)
        else:
            for x in illegal_moves:
                if x not in all_moves:
                    raise Exception(f"illegal move {x} is not in the list of legal moves")

            self.all_moves = []

            for x in all_moves:
                if x not in illegal_moves:
                    self.all_moves.append(x)

        logger.debug(f"{self}: all_moves {','.join(self.all_moves)}")
        COST_LENGTH = 1
        STATE_INDEX_LENGTH = 4
        self.ROW_LENGTH = COST_LENGTH + (STATE_INDEX_LENGTH * len(self.all_moves))

    def get_ida_graph_nodes(self):
        return [pt.ida_graph_node for pt in self.prune_tables]

    def set_ida_graph_nodes(self, ida_graph_nodes) -> None:
        for (pt, node) in zip(self.prune_tables, ida_graph_nodes):
            pt.ida_graph_node = node

    def init_state_index_caches(self) -> None:
        for pt in self.prune_tables:
            pt.load_state_index_cache()

    def init_ida_graph_nodes(self) -> None:
        for pt in self.prune_tables:
            pt.ida_graph_node = pt.state_index()

    def recolor(self):
        """
        re-color the cube per use_nuke_edges, etd and recolor_positions
        """

        if self.nuke_corners or self.nuke_edges or self.nuke_centers or self.recolor_positions:
            logger.info(f"{self}: recolor")
            # self.parent.print_cube("pre recolor")

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

            # self.parent.print_cube("post recolor")
            # sys.exit(0)

    def build_ida_graph_set_cube_state(self, state, steps_to_scramble) -> None:
        # If the table we are building is one with multiple goal states then the
        # child class must override this method.
        self.parent.re_init()
        for step in steps_to_scramble:
            self.parent.rotate(step)

    def build_ida_graph(self, start=None, end=None):
        pt_state_filename = self.filename.replace(".txt", ".pt_state")

        if start is not None:
            pt_state_filename += f"-{start}-{end}"

        for pt in self.prune_tables:
            pt.load_ida_graph()

        to_write = []
        self.init_state_index_caches()

        with open(pt_state_filename, "w") as fh_pt_state:
            with open(self.filename, "r") as fh:
                for (line_number, line) in enumerate(fh):

                    if start is not None and line_number < start:
                        continue

                    if end is not None and line_number > end:
                        break

                    (state, steps_to_solve) = line.rstrip().split(":")
                    steps_to_solve = steps_to_solve.split()

                    if state in self.state_target:
                        cost_to_goal = 0
                    else:
                        cost_to_goal = len(steps_to_solve)

                    steps_to_scramble = reverse_steps(steps_to_solve)
                    self.build_ida_graph_set_cube_state(state, steps_to_scramble)
                    self.init_ida_graph_nodes()
                    pt_ida_graph_nodes = self.get_ida_graph_nodes()

                    lt_state = ""

                    for x in pt_ida_graph_nodes:
                        assert x <= 9999999
                        lt_state += f"{x:07d}-"

                    lt_state = lt_state.rstrip("-")
                    to_write.append(f"{lt_state}:{cost_to_goal}")

                    if line_number and line_number % 100000 == 0:
                        fh_pt_state.write("\n".join(to_write) + "\n")
                        to_write = []

                        if start is not None:
                            logger.info(f"{start:,}->{end:,} line {line_number:,}")
                        else:
                            logger.info(f"line {line_number:,}")

            if to_write:
                fh_pt_state.write("\n".join(to_write) + "\n")
                to_write = []

    def solutions_via_c(
        self,
        pt_states=[],
        min_ida_threshold: int = None,
        max_ida_threshold: int = None,
        solution_count: int = None,
        find_extra: bool = False,
        use_kociemba_string: bool = False,
    ) -> List[List[str]]:
        cmd = ["./ida_search_via_graph"]

        if pt_states:
            pt_states = sorted(set(pt_states))
            pt_states_filename = (
                "/tmp/pt-states-" + "".join(random.choice(string.ascii_uppercase) for i in range(6)) + ".txt"
            )

            for (index, pt) in enumerate(self.prune_tables):
                cmd.append("--prune-table-%d-filename" % index)
                cmd.append(pt.filename_bin)

            with open(pt_states_filename, "w") as fh:
                for x in pt_states:
                    fh.write(",".join(map(str, x)) + "\n")
            cmd.append("--prune-table-states")
            cmd.append(pt_states_filename)
        else:
            self.init_ida_graph_nodes()
            pt_states_filename = None

            for (index, pt) in enumerate(self.prune_tables):
                cmd.append("--prune-table-%d-filename" % index)
                cmd.append(pt.filename_bin)

                if not pt_states:
                    cmd.append("--prune-table-%d-state" % index)
                    cmd.append(str(pt.ida_graph_node))

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
                raise Exception(f"avoid_oll is only supported for orbits 0 or 1, not {self.avoid_oll}")

        # If this is a lookup table that is staging a pair of colors (such as U and D) then recolor the cubies accordingly.
        pre_recolor_state = self.parent.state[:]
        pre_recolor_solution = self.parent.solution[:]
        self.recolor()

        if use_kociemba_string:
            kociemba_string = self.parent.get_kociemba_string(True)
            cmd.append("--kociemba")
            cmd.append(kociemba_string)

        if self.perfect_hash01_filename:
            cmd.append("--prune-table-perfect-hash01")
            cmd.append(self.perfect_hash01_filename)
            cmd.append("--pt1-state-max")
            cmd.append(str(self.pt1_state_max))

        if self.perfect_hash02_filename:
            cmd.append("--prune-table-perfect-hash02")
            cmd.append(self.perfect_hash02_filename)
            cmd.append("--pt2-state-max")
            cmd.append(str(self.pt2_state_max))

        if self.perfect_hash12_filename:
            cmd.append("--prune-table-perfect-hash12")
            cmd.append(self.perfect_hash12_filename)
            cmd.append("--pt2-state-max")
            cmd.append(str(self.pt2_state_max))

        if self.perfect_hash34_filename:
            cmd.append("--prune-table-perfect-hash34")
            cmd.append(self.perfect_hash34_filename)
            cmd.append("--pt4-state-max")
            cmd.append(str(self.pt4_state_max))

        if min_ida_threshold is not None:
            cmd.append("--min-ida-threshold")
            cmd.append(str(min_ida_threshold))

        if max_ida_threshold is not None:
            cmd.append("--max-ida-threshold")
            cmd.append(str(max_ida_threshold))

        if self.centers_only:
            cmd.append("--centers-only")

        if self.use_uthash:
            cmd.append("--uthash")

        if self.C_ida_type is not None:
            cmd.append("--type")
            cmd.append(self.C_ida_type)

        if solution_count is not None:
            cmd.append("--solution-count")
            cmd.append(str(solution_count))

        if find_extra:
            cmd.append("--find-extra")

        cmd.append("--legal-moves")
        cmd.append(",".join(self.all_moves))

        # wrap the X,Y,Z part of "--legal-moves X,Y,Z" in double quotes
        cmd_string = " ".join(cmd)
        cmd_string = cmd_string.replace("--legal-moves ", '--legal-moves "')
        cmd_string += '"'

        if self.multiplier:
            cmd_string += f" --multiplier {self.multiplier}"
            cmd.append("--multiplier")
            cmd.append(str(self.multiplier))

        logger.info(f"{self}: solving via C ida_search\n{cmd_string}\n")
        output = subprocess.check_output(cmd).decode("utf-8")
        output = "\n".join(remove_failed_ida_output(output.splitlines()))
        self.parent.solve_via_c_output = f"\n{cmd_string}\n{output}\n"
        logger.info(f"\n{output}\n\n")

        if pt_states_filename is not None:
            os.unlink(pt_states_filename)

        solutions = []
        pt0_state = None
        pt1_state = None
        pt2_state = None
        pt3_state = None
        pt4_state = None
        self.parent.state = pre_recolor_state[:]
        self.parent.solution = pre_recolor_solution[:]
        RE_PT_STATES = re.compile(
            r"pt0_state (\d+), pt1_state (\d+), pt2_state (\d+), pt3_state (\d+), pt4_state (\d+)"
        )

        for line in output.splitlines():
            match = RE_PT_STATES.search(line)

            if match:
                pt0_state = int(match.group(1))
                pt1_state = int(match.group(2))
                pt2_state = int(match.group(3))
                pt3_state = int(match.group(4))
                pt4_state = int(match.group(5))

            elif line.startswith("SOLUTION"):
                solution = tuple(line.split(":")[1].strip().split())
                solutions.append((len(solution), solution, (pt0_state, pt1_state, pt2_state, pt3_state, pt4_state)))

        if solutions:
            # sort so the shortest solutions are first
            solutions.sort()

            # chop the solutions length
            solutions = [x[1:3] for x in solutions]
            return solutions
        else:
            raise NoIDASolution(f"Did not find SOLUTION line in\n{output}\n")

    def solve_via_c(
        self,
        pt_states=[],
        min_ida_threshold: int = None,
        max_ida_threshold: int = None,
        solution_count: int = None,
        find_extra: bool = False,
        use_kociemba_string: bool = False,
    ) -> None:
        solution = self.solutions_via_c(
            pt_states=pt_states,
            min_ida_threshold=min_ida_threshold,
            max_ida_threshold=max_ida_threshold,
            solution_count=solution_count,
            find_extra=find_extra,
            use_kociemba_string=use_kociemba_string,
        )[0][0]

        for step in solution:
            self.parent.rotate(step)
