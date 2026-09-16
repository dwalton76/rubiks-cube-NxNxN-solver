"""Helpers shared by the utils/build-*-matrix.py samplers."""

from __future__ import annotations

# standard libraries
import unittest

# rubiks cube libraries
from rubikscubennnsolver.heuristic_matrix import fill_cost_matrix, parse_ida_summary_path


class ParseIdaSummaryPathTests(unittest.TestCase):
    def test_it_reads_init_and_later_rows(self):
        output = "\n".join(
            [
                "header junk",
                " INIT    2    4    7   11    0",
                "   U2    2    3    6   10    1",
                "not a row",
            ]
        )
        self.assertEqual(
            parse_ida_summary_path(output, token_count=6, value_indexes=(0, 1, 3)),
            [(2, 4, 11), (2, 3, 10)],
        )


class FillCostMatrixTests(unittest.TestCase):
    def test_it_uses_the_min_remaining_and_propagates(self):
        matrix, counts = fill_cost_matrix(
            [(1, 2, 5), (1, 2, 8)],
            (3, 4),
            lambda index: max(index),
        )
        self.assertEqual(counts[(1, 2)], 2)
        self.assertEqual(matrix[1][2], 5)
        self.assertGreaterEqual(matrix[2][2], 5)
        self.assertGreaterEqual(matrix[1][3], 5)

    def test_empty_cells_stay_at_least_the_admissible_floor(self):
        matrix, counts = fill_cost_matrix([], (2, 3), lambda index: max(index), fallback_multiplier=1.0)
        self.assertEqual(counts[(1, 2)], 0)
        self.assertEqual(matrix[1][2], 2)

    def test_axis_permutations_fill_every_ordering(self):
        matrix, counts = fill_cost_matrix(
            [(1, 0, 2, 9)],
            (3, 3, 3),
            lambda index: max(index),
            permute_coords=True,
        )
        self.assertEqual(counts[(1, 0, 2)], 1)
        self.assertEqual(counts[(2, 1, 0)], 1)
        self.assertEqual(matrix[1][0][2], 9)
        self.assertEqual(matrix[2][1][0], 9)


if __name__ == "__main__":
    unittest.main()
