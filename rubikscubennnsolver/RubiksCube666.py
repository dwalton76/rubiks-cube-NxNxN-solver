"""
6x6x6 solver: reduce the cube to a 5x5x5, then finish with the 5x5x5 solver.

A 6x6x6 has 96 centers (16 per face: four inner x-centers, four outer x-centers,
and eight oblique edges), two orbits of wings, and 8 corners. Reduction solves
the inner x-centers, pairs every oblique pair, and pairs the inside orbit of
wings so the remaining puzzle is a 5x5x5. ``RubiksCube666.reduce_555`` does
that reduction; ``group_edges`` (via the 5x5x5 solver) then pairs the outer
wings and ``solve_333`` finishes the cube.

Each IDA phase is guided by prune tables. Phases 2 and 3 are searched as a
portfolio: many solutions of the earlier phase are collected, later phases
are solved from those endpoints, and the shortest combined path is kept.

Phase 1 - stage all inner x-centers and pair the LR obliques
    Stage all 24 inner x-centers and pair the LR obliques using a ranked
    cost-only table. This phase owns orbit-1 OLL: later phases cannot flip
    that orbit because they must keep the inner x-centers staged (no 3Xw
    quarter turns).

Phase 2 - stage the remaining LR centers
    Map the outer 5x5 of each face onto a fake 5x5x5 and stage its LR
    centers. ``stage_LR_and_UD_centers`` takes a portfolio of those solutions
    (default 64) and searches phase 3 from all distinct endpoints in one C
    process.

Phase 3 - stage UD left/right obliques and outer x-centers
    Ranked pairwise tables move the UD left/right obliques and outer x-centers
    onto U/D. This phase owns orbit-0 OLL. The search keeps the shortest
    phase-2 plus phase-3 pair.

Phase 5 - daisy-solve all centers
    Eighteen overlapping 70^4 ranked tables (one complete axis plus one
    foreign orbit) guide a dedicated C IDA. That pairs every oblique and
    solves every inner x-center. Outer x-centers are left for the 5x5x5.

Phase 6 - EO the inside wings
    The inside wings are then paired by ``pair_inside_edges_via_444``, which maps
    the 6x6x6 slices a 4x4x4 can see onto a fake 4x4x4 and runs the whole 4x4x4
    reduction on it. That is where the inside wings get EOed, so the 6x6x6 needs
    no EO phase of its own. Those moves leave the daisy intact because the fake
    4x4x4 ends with its own centers solved.
"""

# standard libraries
import logging
import os
import subprocess
import sys
import tempfile

# rubiks cube libraries
from rubikscubennnsolver import SolveError
from rubikscubennnsolver.LookupTable import download_file_if_needed
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
from rubikscubennnsolver.RubiksCubeNNNEvenEdges import RubiksCubeNNNEvenEdges
from rubikscubennnsolver.swaps import swaps_666

logger = logging.getLogger(__name__)


# fmt: off
moves_666 = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",
    "F", "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",
    "R", "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",
    "B", "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",
    "D", "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2",
    # slices...not used for now
    # "2U", "2U'", "2U2", "2D", "2D'", "2D2",
    # "2L", "2L'", "2L2", "2R", "2R'", "2R2",
    # "2F", "2F'", "2F2", "2B", "2B'", "2B2",
    # "3U", "3U'", "3U2", "3D", "3D'", "3D2",
    # "3L", "3L'", "3L2", "3R", "3R'", "3R2",
    # "3F", "3F'", "3F2", "3B", "3B'", "3B2"
)
solved_666 = "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

corners_666 = (
    1, 6, 31, 36,
    37, 42, 67, 72,
    73, 78, 103, 108,
    109, 114, 139, 144,
    145, 150, 175, 180,
    181, 186, 211, 216,
)

inner_x_centers_666 = (
    15, 16, 21, 22,  # Upper
    51, 52, 57, 58,  # Left
    87, 88, 93, 94,  # Front
    123, 124, 129, 130,  # Right
    159, 160, 165, 166,  # Back
    195, 196, 201, 202,  # Down
)

outer_x_centers_666 = (
    8, 11, 26, 29,
    44, 47, 62, 65,
    80, 83, 98, 101,
    116, 119, 134, 137,
    152, 155, 170, 173,
    188, 191, 206, 209,
)

centers_666 = (
    8, 9, 10, 11, 14, 15, 16, 17, 20, 21, 22, 23, 26, 27, 28, 29,  # Upper
    44, 45, 46, 47, 50, 51, 52, 53, 56, 57, 58, 59, 62, 63, 64, 65,  # Left
    80, 81, 82, 83, 86, 87, 88, 89, 92, 93, 94, 95, 98, 99, 100, 101,  # Front
    116, 117, 118, 119, 122, 123, 124, 125, 128, 129, 130, 131, 134, 135, 136, 137,  # Right
    152, 153, 154, 155, 158, 159, 160, 161, 164, 165, 166, 167, 170, 171, 172, 173,  # Back
    188, 189, 190, 191, 194, 195, 196, 197, 200, 201, 202, 203, 206, 207, 208, 209,  # Down
)

oblique_edges_666 = (
    9, 10, 14, 17, 20, 23, 27, 28,  # Upper
    45, 46, 50, 53, 56, 59, 63, 64,  # Left
    81, 82, 86, 89, 92, 95, 99, 100,  # Front
    117, 118, 122, 125, 128, 131, 135, 136,  # Right
    153, 154, 158, 161, 164, 167, 171, 172,  # Back
    189, 190, 194, 197, 200, 203, 207, 208,  # Down
)

left_oblique_edges_666 = (
    9, 17, 28, 20,
    45, 53, 64, 56,
    81, 89, 100, 92,
    117, 125, 136, 128,
    153, 161, 172, 164,
    189, 197, 208, 200,
)

right_oblique_edges_666 = (
    10, 23, 27, 14,
    46, 59, 63, 50,
    82, 95, 99, 86,
    118, 131, 135, 122,
    154, 167, 171, 158,
    190, 203, 207, 194,
)

UFBD_left_oblique_edges_666 = (
    9, 17, 20, 28,  # Upper
    81, 89, 92, 100,  # Front
    153, 161, 164, 172,  # Back
    189, 197, 200, 208,  # Down
)

UFBD_right_oblique_edges_666 = (
    10, 14, 23, 27,  # Upper
    82, 86, 95, 99,  # Front
    154, 158, 167, 171,  # Back
    190, 194, 203, 207,  # Down
)

UFBD_outer_x_centers_666 = (
    8, 11, 26, 29,  # Upper
    80, 83, 98, 101,  # Front
    152, 155, 170, 173,  # Back
    188, 191, 206, 209,  # Down
)

UFBD_inner_x_centers_666 = (
    15, 16, 21, 22,  # Upper
    87, 88, 93, 94,  # Front
    159, 160, 165, 166,  # Back
    195, 196, 201, 202,  # Down
)

edge_orbit_0 = (
    2, 5, 12, 30, 35, 32, 25, 7,
    38, 41, 48, 66, 71, 68, 61, 43,
    74, 77, 84, 102, 107, 104, 97, 79,
    110, 113, 120, 138, 143, 140, 133, 115,
    146, 149, 156, 174, 179, 176, 169, 151,
    182, 185, 192, 210, 215, 212, 205, 187,
)

edge_orbit_1 = (
    3, 4, 18, 24, 34, 33, 19, 13,
    39, 40, 54, 60, 70, 69, 55, 49,
    75, 76, 90, 96, 106, 105, 91, 85,
    111, 112, 126, 132, 142, 141, 127, 121,
    147, 148, 162, 168, 178, 177, 163, 157,
    183, 184, 198, 204, 214, 213, 199, 193,
)

edges_partner_666 = {
    2: 149,
    3: 148,
    4: 147,
    5: 146,
    7: 38,
    12: 113,
    13: 39,
    18: 112,
    19: 40,
    24: 111,
    25: 41,
    30: 110,
    32: 74,
    33: 75,
    34: 76,
    35: 77,
    38: 7,
    39: 13,
    40: 19,
    41: 25,
    43: 156,
    48: 79,
    49: 162,
    54: 85,
    55: 168,
    60: 91,
    61: 174,
    66: 97,
    68: 205,
    69: 199,
    70: 193,
    71: 187,
    74: 32,
    75: 33,
    76: 34,
    77: 35,
    79: 48,
    84: 115,
    85: 54,
    90: 121,
    91: 60,
    96: 127,
    97: 66,
    102: 133,
    104: 182,
    105: 183,
    106: 184,
    107: 185,
    110: 30,
    111: 24,
    112: 18,
    113: 12,
    115: 84,
    120: 151,
    121: 90,
    126: 157,
    127: 96,
    132: 163,
    133: 102,
    138: 169,
    140: 192,
    141: 198,
    142: 204,
    143: 210,
    146: 5,
    147: 4,
    148: 3,
    149: 2,
    151: 120,
    156: 43,
    157: 126,
    162: 49,
    163: 132,
    168: 55,
    169: 138,
    174: 61,
    176: 215,
    177: 214,
    178: 213,
    179: 212,
    182: 104,
    183: 105,
    184: 106,
    185: 107,
    187: 71,
    192: 140,
    193: 70,
    198: 141,
    199: 69,
    204: 142,
    205: 68,
    210: 143,
    212: 179,
    213: 178,
    214: 177,
    215: 176,
}
# fmt: on


# fmt: off
PHASE5_ILLEGAL_MOVES = (
    "3Rw", "3Rw'",
    "3Lw", "3Lw'",
    "3Fw", "3Fw'",
    "3Bw", "3Bw'",
    "3Uw", "3Uw'",
    "3Dw", "3Dw'",
    "Rw", "Rw'",
    "Lw", "Lw'",
    "Fw", "Fw'",
    "Bw", "Bw'",
    "Uw", "Uw'",
    "Dw", "Dw'",
)

# fmt: on


# ==================================================
# phase 1
# stage all inner x-centers and pair the LR obliques
# ==================================================
ALL_INNER_X_CENTERS_STAGE_TABLE = (
    "lookup-tables/lookup-table-6x6x6-step05-inner-x-centers-stage-one-phase.cost-only.bin"
)


class LookupTableIDA666InnerXCentersStageOnePhase:
    """
    Stage all 24 inner x-centers in one phase (8 UD, 8 LR, 8 FB).

    24! / (8!^3) = 9,465,511,770 states. Built as a ranked cost-only table.

                 . . . . . .
                 . . . . . .
                 . . U U . .
                 . . U U . .
                 . . . . . .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . L L . .  . . F F . .  . . L L . .  . . F F . .
    . . L L . .  . . F F . .  . . L L . .  . . F F . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . . . . . .
                 . . U U . .
                 . . U U . .
                 . . . . . .
                 . . . . . .
    """

    def __init__(self, parent):
        self.parent = parent
        self.filename = ALL_INNER_X_CENTERS_STAGE_TABLE
        self.avoid_oll = None
        download_file_if_needed(self.filename)

    def solve_via_c(self, unpaired_multiplier=None) -> None:
        cmd = [
            "./ida_search_666_centers_stage",
            "--kociemba",
            self.parent.get_kociemba_string(True),
            "--all-inner-x-cost",
            self.filename,
        ]
        if unpaired_multiplier is not None:
            cmd.extend(("--unpaired-multiplier", str(unpaired_multiplier)))

        if self.avoid_oll is not None:
            orbits_with_oll = self.parent.center_solution_leads_to_oll_parity()
            if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
                cmd.append("--orbit0-need-odd-w" if 0 in orbits_with_oll else "--orbit0-need-even-w")
            if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
                cmd.append("--orbit1-need-odd-w" if 1 in orbits_with_oll else "--orbit1-need-even-w")

        logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
        lines = []
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        ) as proc:
            for line in proc.stdout:
                lines.append(line)
                logger.info("%s", line.rstrip("\n"))
            returncode = proc.wait()

        output = "".join(lines)
        self.parent.solve_via_c_output = output
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                for step in line.split(":", 1)[1].strip().split():
                    self.parent.rotate(step)
                return

        raise SolveError(f"ida_search_666_centers_stage failed with exit {returncode}\n{output}")


# ==================================================
# phase 2
# stage the remaining LR centers via a fake 5x5x5
# ==================================================


# ==================================================
# phase 3
# stage UD left/right obliques and outer x-centers
# ==================================================
class LookupTable666RankedPhase3:
    """Describe a dense pairwise ranked-cost table used by the phase-3 IDA."""

    def __init__(self, parent, filename):
        self.parent = parent
        self.filename = "lookup-tables/" + filename
        download_file_if_needed(self.filename)


class LookupTable666UDLeftRightObliqueStage(LookupTable666RankedPhase3):
    """
    (16! / (8! * 8!))^2 = 165,636,900 states

                 . . . . . .
                 . . U U . .
                 . U . . U .
                 . U . . U .
                 . . U U . .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . . x x . .  . . . . . .  . . x x . .
    . . . . . .  . x . . x .  . . . . . .  . x . . x .
    . . . . . .  . x . . x .  . . . . . .  . x . . x .
    . . . . . .  . . x x . .  . . . . . .  . . x x . .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . . U U . .
                 . U . . U .
                 . U . . U .
                 . . U U . .
                 . . . . . .
    """

    def __init__(self, parent):
        LookupTable666RankedPhase3.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step31-UD-left-right-oblique-centers-stage.cost-only.bin",
        )


class LookupTable666UDLeftObliqueOuterXStage(LookupTable666RankedPhase3):
    """
    (16! / (8! * 8!))^2 = 165,636,900 states

                 . . . . . .
                 . U U . U .
                 . . . . U .
                 . U . . . .
                 . U . U U .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . x x . x .  . . . . . .  . x x . x .
    . . . . . .  . . . . x .  . . . . . .  . . . . x .
    . . . . . .  . x . . . .  . . . . . .  . x . . . .
    . . . . . .  . x . x x .  . . . . . .  . x . x x .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . U U . U .
                 . . . . U .
                 . U . . . .
                 . U . U U .
                 . . . . . .
    """

    def __init__(self, parent):
        LookupTable666RankedPhase3.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step32-UD-left-oblique-outer-x-centers-stage.cost-only.bin",
        )


class LookupTable666UDRightObliqueOuterXStage(LookupTable666RankedPhase3):
    """
    (16! / (8! * 8!))^2 = 165,636,900 states

                 . . . . . .
                 . U . U U .
                 . U . . . .
                 . . . . U .
                 . U U . U .
                 . . . . . .

    . . . . . .  . . . . . .  . . . . . .  . . . . . .
    . . . . . .  . x . x x .  . . . . . .  . x . x x .
    . . . . . .  . x . . . .  . . . . . .  . x . . . .
    . . . . . .  . . . . x .  . . . . . .  . . . . x .
    . . . . . .  . x x . x .  . . . . . .  . x x . x .
    . . . . . .  . . . . . .  . . . . . .  . . . . . .

                 . . . . . .
                 . U . U U .
                 . U . . . .
                 . . . . U .
                 . U U . U .
                 . . . . . .
    """

    def __init__(self, parent):
        LookupTable666RankedPhase3.__init__(
            self,
            parent,
            "lookup-table-6x6x6-step33-UD-right-oblique-outer-x-centers-stage.cost-only.bin",
        )


class LookupTableIDA666UDCentersStage:
    def __init__(self, parent):
        self.parent = parent
        self.avoid_oll = None

    def solution_via_c(self, roots=None):
        cmd = [
            "./ida_search_666_centers_stage",
            "--left-right-oblique-cost",
            self.parent.lt_UD_left_right_oblique_stage.filename,
            "--left-oblique-outer-x-cost",
            self.parent.lt_UD_left_oblique_outer_x_stage.filename,
            "--right-oblique-outer-x-cost",
            self.parent.lt_UD_right_oblique_outer_x_stage.filename,
        ]

        roots_filename = None
        if roots:
            with tempfile.NamedTemporaryFile(mode="w", prefix="666-centers-roots-", suffix=".txt", delete=False) as fh:
                roots_filename = fh.name
                for root_index, kociemba, orbits_with_oll in roots:
                    orbit0_requirement = 0
                    orbit1_requirement = 0
                    if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
                        orbit0_requirement = 1 if 0 in orbits_with_oll else 2
                    if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
                        orbit1_requirement = 1 if 1 in orbits_with_oll else 2
                    fh.write(f"{root_index},{orbit0_requirement},{orbit1_requirement},{kociemba}\n")
            cmd.extend(("--kociemba-file", roots_filename))
        else:
            cmd.extend(("--kociemba", self.parent.get_kociemba_string(True)))

        if not roots and self.avoid_oll is not None:
            orbits_with_oll = self.parent.center_solution_leads_to_oll_parity()
            if self.avoid_oll == 0 or self.avoid_oll == (0, 1):
                cmd.append("--orbit0-need-odd-w" if 0 in orbits_with_oll else "--orbit0-need-even-w")
            if self.avoid_oll == 1 or self.avoid_oll == (0, 1):
                cmd.append("--orbit1-need-odd-w" if 1 in orbits_with_oll else "--orbit1-need-even-w")

        try:
            logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
            lines = []
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            ) as proc:
                for line in proc.stdout:
                    lines.append(line)
                    logger.info("%s", line.rstrip("\n"))
                returncode = proc.wait()
        finally:
            if roots_filename is not None:
                os.unlink(roots_filename)

        output = "".join(lines)
        self.parent.solve_via_c_output = output
        root_index = 0
        for line in output.splitlines():
            if line.startswith("ROOT_INDEX "):
                root_index = int(line.split()[1])
            if line.startswith("SOLUTION"):
                return root_index, tuple(line.split(":", 1)[1].strip().split())

        raise SolveError(f"ida_search_666_centers_stage failed with exit {returncode}\n{output}")

    def solve_via_c(self) -> None:
        _, solution = self.solution_via_c()
        for step in solution:
            self.parent.rotate(step)


# ==================================================
# phase 5
# daisy-solve all centers with overlapping 70^4 ranked tables
# ==================================================
DAISY_PLUS_TABLES_666 = tuple(
    (
        f"--{axis.lower()}-plus-{extra_axis.lower()}-{orbit}-cost",
        f"lookup-tables/lookup-table-6x6x6-daisy-{axis}-plus-{extra_axis}-{orbit}-centers.cost-only.bin",
    )
    for axis in ("UD", "LR", "FB")
    for extra_axis in ("UD", "LR", "FB")
    if extra_axis != axis
    for orbit in ("left-oblique", "right-oblique", "inner-x")
)


class LookupTableIDA666DaisyCenters:
    """
    Daisy-solve remaining centers with eighteen mixed-axis 70^4 ranked tables.

    Each table is 24,010,000 states. Extra-oblique tables top out at 12 moves
    (average 8.50); extra inner-x tables top out at 13 (average 9.43).
    """

    def __init__(self, parent, multiplier=None):
        self.parent = parent
        self.avoid_oll = None
        self.multiplier = multiplier

    def solve_via_c(self, **_kwargs):
        cmd = ["./ida_search_666_daisy_centers", "--kociemba", self.parent.get_kociemba_string(True)]
        for flag, filename in DAISY_PLUS_TABLES_666:
            download_file_if_needed(filename)
            cmd.extend((flag, filename))
        if self.multiplier:
            cmd.extend(("--multiplier", str(self.multiplier)))

        logger.info("%s: solving via C\n%s", self.__class__.__name__, " ".join(cmd))
        lines = []
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        ) as proc:
            for line in proc.stdout:
                lines.append(line)
                logger.info("%s", line.rstrip("\n"))
            returncode = proc.wait()

        output = "".join(lines)
        self.parent.solve_via_c_output = output
        for line in output.splitlines():
            if line.startswith("SOLUTION"):
                for step in line.split(":", 1)[1].strip().split():
                    self.parent.rotate(step)
                return

        raise SolveError(f"ida_search_666_daisy_centers failed with exit {returncode}\n{output}")


class RubiksCube666(RubiksCubeNNNEvenEdges):
    """
    6x6x6 strategy
    - stage LR centers to sides L or R (use IDA)
    - stage UD centers to sides U or D...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3

    Inheritance model
    -----------------
            RubiksCube
                |
        RubiksCubeNNNEvenEdges
           /            \
    RubiksCubeNNNEven RubiksCube666
    """

    reduce333_orient_edges_tuples = (
        (2, 149),
        (3, 148),
        (4, 147),
        (5, 146),
        (7, 38),
        (12, 113),
        (13, 39),
        (18, 112),
        (19, 40),
        (24, 111),
        (25, 41),
        (30, 110),
        (32, 74),
        (33, 75),
        (34, 76),
        (35, 77),
        (38, 7),
        (39, 13),
        (40, 19),
        (41, 25),
        (43, 156),
        (48, 79),
        (49, 162),
        (54, 85),
        (55, 168),
        (60, 91),
        (61, 174),
        (66, 97),
        (68, 205),
        (69, 199),
        (70, 193),
        (71, 187),
        (74, 32),
        (75, 33),
        (76, 34),
        (77, 35),
        (79, 48),
        (84, 115),
        (85, 54),
        (90, 121),
        (91, 60),
        (96, 127),
        (97, 66),
        (102, 133),
        (104, 182),
        (105, 183),
        (106, 184),
        (107, 185),
        (110, 30),
        (111, 24),
        (112, 18),
        (113, 12),
        (115, 84),
        (120, 151),
        (121, 90),
        (126, 157),
        (127, 96),
        (132, 163),
        (133, 102),
        (138, 169),
        (140, 192),
        (141, 198),
        (142, 204),
        (143, 210),
        (146, 5),
        (147, 4),
        (148, 3),
        (149, 2),
        (151, 120),
        (156, 43),
        (157, 126),
        (162, 49),
        (163, 132),
        (168, 55),
        (169, 138),
        (174, 61),
        (176, 215),
        (177, 214),
        (178, 213),
        (179, 212),
        (182, 104),
        (183, 105),
        (184, 106),
        (185, 107),
        (187, 71),
        (192, 140),
        (193, 70),
        (198, 141),
        (199, 69),
        (204, 142),
        (205, 68),
        (210, 143),
        (212, 179),
        (213, 178),
        (214, 177),
        (215, 176),
    )

    def get_fake_444(self):
        if self.fake_444 is None:
            self.fake_444 = RubiksCube444(solved_444, "URFDLB")
            self.fake_444.lt_init()
            self.fake_444.enable_print_cube = False
        else:
            self.fake_444.re_init()
        return self.fake_444

    def get_fake_555(self):
        if self.fake_555 is None:
            self.fake_555 = RubiksCube555(solved_555, "URFDLB", use_one_phase_centers_stage=False)
            self.fake_555.lt_init()
            self.fake_555.enable_print_cube = False

        else:
            self.fake_555.re_init()
        return self.fake_555

    def print_edge_tuples(self):
        edge_indexes = list(edge_orbit_0) + list(edge_orbit_1)
        edge_indexes.sort()

        for count, square_index in enumerate(edge_indexes):
            if count % 16 == 0:
                print("")

            # Used to build edges_partner_666
            # side = self.index_to_side[square_index]
            # partner_index = side.get_wing_partner(square_index)
            # print("    %d: %d," % (square_index, partner_index))

            partner_index = edges_partner_666[square_index]
            sys.stdout.write("(%d, %d), " % (square_index, partner_index))

        print("")

    def sanity_check(self):
        self._sanity_check("edge-orbit-0", edge_orbit_0, 8)
        self._sanity_check("edge-orbit-1", edge_orbit_1, 8)
        self._sanity_check("corners", corners_666, 4)
        self._sanity_check("left-oblique", left_oblique_edges_666, 4)
        self._sanity_check("right-oblique", right_oblique_edges_666, 4)
        self._sanity_check("outside x-center", outer_x_centers_666, 4)
        self._sanity_check("inside x-center", inner_x_centers_666, 4)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # phase 1 - stage all inner x-centers and pair LR obliques
        self.lt_all_inner_x_centers_stage = LookupTableIDA666InnerXCentersStageOnePhase(self)

        # Phases 2 and 3 must preserve the staged inner x-centers, which
        # rules out every 3Xw quarter turn, so this is the only phase that
        # can still flip orbit1 parity.
        self.lt_all_inner_x_centers_stage.avoid_oll = 1

        # phase 3 - ranked UD oblique + outer-x tables to finish staging UD
        self.lt_UD_left_right_oblique_stage = LookupTable666UDLeftRightObliqueStage(self)
        self.lt_UD_left_oblique_outer_x_stage = LookupTable666UDLeftObliqueOuterXStage(self)
        self.lt_UD_right_oblique_outer_x_stage = LookupTable666UDRightObliqueOuterXStage(self)
        self.lt_UD_centers_stage = LookupTableIDA666UDCentersStage(self)

        # Only orbit0 here; phase 1 owns orbit1 for the reason above.
        self.lt_UD_centers_stage.avoid_oll = 0

        # phase 5 - daisy-solve all centers with overlapping 70^4 ranked tables
        self.lt_daisy_centers = LookupTableIDA666DaisyCenters(self)

    def populate_fake_555_for_ULFRBD_solve(self):
        fake_555 = self.get_fake_555()
        fake_555.nuke_corners()
        fake_555.nuke_edges()
        fake_555.nuke_centers()
        side_names = ("U", "L", "F", "R", "B", "D")

        for side_index in range(6):
            offset_555 = side_index * 25
            offset_666 = side_index * 36
            side_name = side_names[side_index]

            # corners
            fake_555.state[1 + offset_555] = self.state[1 + offset_666]
            fake_555.state[5 + offset_555] = self.state[6 + offset_666]
            fake_555.state[21 + offset_555] = self.state[31 + offset_666]
            fake_555.state[25 + offset_555] = self.state[36 + offset_666]

            # centers
            fake_555.state[7 + offset_555] = self.state[8 + offset_666]
            fake_555.state[8 + offset_555] = self.state[9 + offset_666]
            fake_555.state[9 + offset_555] = self.state[11 + offset_666]
            fake_555.state[12 + offset_555] = self.state[14 + offset_666]
            fake_555.state[13 + offset_555] = side_name
            fake_555.state[14 + offset_555] = self.state[17 + offset_666]
            fake_555.state[17 + offset_555] = self.state[26 + offset_666]
            fake_555.state[18 + offset_555] = self.state[27 + offset_666]
            fake_555.state[19 + offset_555] = self.state[29 + offset_666]

            # edges
            fake_555.state[2 + offset_555] = self.state[2 + offset_666]
            fake_555.state[3 + offset_555] = side_name
            fake_555.state[4 + offset_555] = self.state[5 + offset_666]

            fake_555.state[6 + offset_555] = self.state[7 + offset_666]
            fake_555.state[10 + offset_555] = self.state[12 + offset_666]

            fake_555.state[11 + offset_555] = side_name
            fake_555.state[15 + offset_555] = side_name

            fake_555.state[16 + offset_555] = self.state[25 + offset_666]
            fake_555.state[20 + offset_555] = self.state[30 + offset_666]

            fake_555.state[22 + offset_555] = self.state[32 + offset_666]
            fake_555.state[23 + offset_555] = side_name
            fake_555.state[24 + offset_555] = self.state[35 + offset_666]

    def reduced_to_555(self) -> bool:
        if not all([self.state[x] == "U" for x in (15, 16, 21, 22)]):  # Upper
            return False

        if not all([self.state[x] == "L" for x in (51, 52, 57, 58)]):  # Left
            return False

        if not all([self.state[x] == "F" for x in (87, 88, 93, 94)]):  # Front
            return False

        if not all([self.state[x] == "R" for x in (123, 124, 129, 130)]):  # Right
            return False

        if not all([self.state[x] == "B" for x in (159, 160, 165, 166)]):  # Back
            return False

        if not all([self.state[x] == "D" for x in (195, 196, 201, 202)]):  # Down
            return False

        # verify all oblique edges are paired
        # fmt: off
        for (x, y) in (
            (9, 10), (20, 14), (17, 23), (28, 27),  # Upper
            (45, 46), (56, 50), (53, 59), (64, 63),  # Left
            (81, 82), (92, 86), (89, 95), (100, 99),  # Front
            (117, 118), (128, 122), (125, 131), (136, 135),  # Right
            (153, 154), (164, 158), (161, 167), (172, 171),  # Back
            (189, 190), (200, 194), (197, 203), (208, 207),  # Down
        ):
            if self.state[x] != self.state[y]:
                return False

        # verify the inside orbit of edges are paired
        for (x, y) in (
            (3, 4), (18, 24), (34, 33), (19, 13),  # Upper
            (39, 40), (54, 60), (70, 69), (55, 49),  # Left
            (75, 76), (90, 96), (106, 105), (91, 85),  # Front
            (111, 112), (126, 132), (142, 141), (127, 121),  # Right
            (147, 148), (162, 168), (178, 177), (163, 157),  # Back
            (183, 184), (198, 204), (214, 213), (199, 193),  # Down
        ):
            if self.state[x] != self.state[y]:
                return False
        # fmt: on

        return True

    def daisy_solve_centers(self) -> None:
        """Daisy-solve the staged centers with the ranked C search."""
        comment_start = len(self.solution)
        self.lt_daisy_centers.solve_via_c()
        self.print_cube_add_comment("centers reduced to 555", comment_start)

    def stage_LR_and_UD_centers(self, phase2_solution_count: int = 64) -> None:
        """Select the phase-2 endpoint that gives the shortest ranked phase 3."""
        original_state = self.state[:]
        original_solution = self.solution[:]
        phase2_comment_start = len(self.solution)

        fake_555 = self.get_fake_555()
        self.populate_fake_555_for_ULFRBD_solve()
        phase2_solutions = fake_555.lt_LR_centers_stage.solutions_via_c(solution_count=phase2_solution_count)

        phase2_solution_by_root = {}
        root_keys = set()
        roots = []
        phase3_squares = (
            tuple(UFBD_outer_x_centers_666) + tuple(UFBD_left_oblique_edges_666) + tuple(UFBD_right_oblique_edges_666)
        )

        for phase2_solution, _ in phase2_solutions:
            self.state = original_state[:]
            self.solution = original_solution[:]
            for step in phase2_solution:
                self.rotate(step)

            orbits_with_oll = frozenset(self.center_solution_leads_to_oll_parity())
            root_key = (
                tuple(self.state[square] for square in phase3_squares),
                0 in orbits_with_oll,
            )
            if root_key in root_keys:
                continue

            root_index = len(roots)
            root_keys.add(root_key)
            phase2_solution_by_root[root_index] = phase2_solution
            roots.append((root_index, self.get_kociemba_string(True), orbits_with_oll))

        logger.info(
            "phase-2 portfolio has %d solutions and %d distinct phase-3 roots",
            len(phase2_solutions),
            len(roots),
        )
        root_index, phase3_solution = self.lt_UD_centers_stage.solution_via_c(roots)
        phase2_solution = phase2_solution_by_root[root_index]

        self.state = original_state[:]
        self.solution = original_solution[:]
        for step in phase2_solution:
            self.rotate(step)
        self.print_cube_add_comment("LR centers staged", phase2_comment_start)

        phase3_comment_start = len(self.solution)
        for step in phase3_solution:
            self.rotate(step)
        self.print_cube_add_comment("UD centers staged", phase3_comment_start)
        logger.info(
            "selected phase-2 length %d and phase-3 length %d (%d total)",
            len(phase2_solution),
            len(phase3_solution),
            len(phase2_solution) + len(phase3_solution),
        )

    def stage_centers(self):
        """
        Stage all inner x-centers and pair LR obliques, then stage LR and UD
        via a phase-2/3 portfolio. If LR is already staged, only run phase 3.
        """
        if not self.LR_centers_staged():
            tmp_solution_len = len(self.solution)
            self.lt_all_inner_x_centers_stage.solve_via_c()
            self.print_cube_add_comment("inner x-centers staged, LR oblique edges paired", tmp_solution_len)
            self.stage_LR_and_UD_centers()
            return

        if not self.UD_centers_staged():
            tmp_solution_len = len(self.solution)
            self.lt_UD_centers_stage.solve_via_c()
            self.print_cube_add_comment("UD centers staged", tmp_solution_len)

    def reduce_555(self):
        if self.reduced_to_555():
            return

        self.lt_init()
        self.stage_centers()
        self.daisy_solve_centers()
        self.pair_inside_edges_via_444()


def rotate_666(cube, step):
    return [cube[x] for x in swaps_666[step]]
