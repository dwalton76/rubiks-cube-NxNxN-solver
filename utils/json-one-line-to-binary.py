#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import struct
import sys


log = logging.getLogger(__name__)
moves_777 = (
    "U", "U'", "U2", "Uw", "Uw'", "Uw2", "3Uw", "3Uw'", "3Uw2",
    "L", "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",
    "F", "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",
    "R", "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",
    "B", "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",
    "D", "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2",
)


def convert_json_one_line_to_binary(filename: str, state_is_hex: bool) -> None:
    assert filename.endswith(".json-one-line")

    if not os.path.exists(filename):
        print(f"ERROR: {filename} does not exist")
        sys.exit(1)

    # build a dictionary that translates a state to its index among all states
    state_index_filename = filename.replace(".json-one-line", ".state_index")
    state_to_index = {}

    with open(state_index_filename, "r") as fh:
        for line in fh:
            (state, state_index) = line.rstrip().split(":")
            state_to_index[state] = int(state_index)

    binary_filename = filename.replace(".json-one-line", ".bin")

    with open(binary_filename, "wb") as fh_bin:
        with open(filename, "r") as fh:
            for (line_number, line) in enumerate(fh):
                data = eval(line)
                state = list(data.keys())[0]

                node = data[state]
                cost = node["cost"]
                edges = node["edges"]

                # write the cost_to_goal (1 byte)
                fh_bin.write(struct.pack(">B", cost))

                # write all of the step/next_state pairs
                for step in moves_777:
                    next_state = edges.get(step)

                    if next_state:
                        next_state_index = state_to_index[next_state]
                        fh_bin.write(struct.pack(">L", next_state_index))

                if line_number % 100000 == 0:
                    log.info(line_number)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)20s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    filename = sys.argv[1]
    convert_json_one_line_to_binary(filename, True)
