"""Helpers shared by the utils/build-*-matrix.py samplers."""

from __future__ import annotations

# standard libraries
import unittest

# rubiks cube libraries
from rubikscubennnsolver.heuristic_matrix import (
    cell_remaining_estimate,
    fill_cost_matrix,
    parse_ida_summary_path,
)


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

    def test_it_skips_a_minimum_at_or_below_five_percent(self):
        samples = [(0, 0, 8)] + [(0, 0, 9)] * 19
        matrix, counts = fill_cost_matrix(
            samples,
            (1, 1),
            lambda index: 0,
            min_fraction=0.05,
        )
        self.assertEqual(counts[(0, 0)], 20)
        self.assertEqual(matrix[0][0], 9)

    def test_it_keeps_a_minimum_above_five_percent(self):
        samples = [(0, 0, 8)] + [(0, 0, 9)] * 3
        matrix, _ = fill_cost_matrix(
            samples,
            (1, 1),
            lambda index: 0,
            min_fraction=0.05,
        )
        self.assertEqual(matrix[0][0], 8)

    def test_it_keeps_the_min_when_every_value_is_rare(self):
        matrix, _ = fill_cost_matrix(
            [(0, 0, remaining) for remaining in range(20)],
            (1, 1),
            lambda index: 0,
            min_fraction=0.05,
        )
        self.assertEqual(matrix[0][0], 0)


class CellRemainingEstimateTests(unittest.TestCase):
    def test_default_is_min(self):
        self.assertEqual(cell_remaining_estimate([8, 9, 9, 9]), 8)

    def test_skips_a_five_percent_minimum(self):
        self.assertEqual(cell_remaining_estimate([8] + [9] * 19, min_fraction=0.05), 9)

    def test_skips_stacked_rare_minima(self):
        values = [8] + [9] + [10] * 18
        self.assertEqual(cell_remaining_estimate(values, min_fraction=0.05), 10)


if __name__ == "__main__":
    unittest.main()
