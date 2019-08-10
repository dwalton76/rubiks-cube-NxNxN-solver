#!/usr/bin/env python3

import json
import logging
import os
import struct
import sys


log = logging.getLogger(__name__)


def convert_json_to_binary(filename: str, state_is_hex: bool) -> None:
    assert filename.endswith(".json")

    if not os.path.exists(filename):
        print(f"ERROR: {filename} does not exist")
        sys.exit(1)

    # load the json contents
    with open(filename, "r") as fh:
        data = json.load(fh)

    # build a dictionary that translates a state to its index among all states
    states = sorted(data.keys())
    state_to_index = {}

    for (index, state) in enumerate(states):
        state_to_index[state] = index

    state_index_filename = filename.replace(".json", ".state_index")

    with open(state_index_filename, "w") as fh:
        for state in states:
            state_index = state_to_index[state]
            fh.write("%s:%d\n" % (state, state_index))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)20s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    filename = sys.argv[1]
    convert_json_to_binary(filename, True)
