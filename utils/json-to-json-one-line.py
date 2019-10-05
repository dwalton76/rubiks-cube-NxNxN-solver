#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import struct
import sys


log = logging.getLogger(__name__)


def convert_json_to_json_one_line(filename: str, entry_length: int, state_is_hex: bool) -> None:

    if not os.path.exists(filename):
        print(f"ERROR: {filename} does not exist")
        sys.exit(1)

    # You must define this!! This is how many lines long an entry is in the .json file you are converting
    assert entry_length > 1

    one_line_filename = filename.replace(".json", ".json-one-line")
    with open(one_line_filename, "w") as fh_one_line:
        with open(filename, "r") as fh:
            # The first line in the opening {, skip it
            next(fh);
            i = 0

            while True:
                data_str = ""

                try:
                    for x in range(entry_length):
                        data_str += next(fh).rstrip()
                except StopIteration:
                    break
                data_str = data_str.lstrip()
                data_str = data_str.rstrip(",")
                fh_one_line.write("{" + data_str + "}\n")

                i += 1

                if i % 100000 == 0:
                    log.info(i)

    subprocess.call("LC_ALL=C nice sort --temporary-directory=./tmp/ --output %s %s" % (one_line_filename, one_line_filename), shell=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)20s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    filename = sys.argv[1]
    entry_length = int(sys.argv[2])
    convert_json_to_json_one_line(filename, entry_length, True)
