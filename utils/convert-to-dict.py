#!/usr/bin/env python3

import logging
import os
import sys

log = logging.getLogger(__name__)


def convert_to_dict(filename):
    filename_new = filename.replace('.txt', '.dict.py')

    with open(filename_new, 'w') as fh_new:
        fh_new.write("{\n")
        first = True

        with open(filename, 'r') as fh:
            for (line_number, line) in enumerate(fh):
                (state, steps) = line.strip().split(':')

                if first:
                    first = False
                    fh_new.write("\n")
                else:
                    fh_new.write(",\n")

                fh_new.write('"%s" : "%s"' % (state, steps))
        fh_new.write("\n}\n")


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("ERROR: To use './convert-to-dict.py FILENAME'")
        sys.exit(1)

    filename = sys.argv[1]

    if not os.path.isfile(filename):
        print("ERROR: %s does not exist" % filename)
        sys.exit(1)

    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    convert_to_dict(filename)
