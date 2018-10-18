#!/usr/bin/env python

# See this post
# http://cubesolvingprograms.freeforums.net/thread/12/number-5x5x5-positions-function-depth?page=2&scrollTo=717

def gods_number(size, MOVE_COUNT, COMBOS):
    prev_depth = MOVE_COUNT
    total = MOVE_COUNT

    PADDING = len(str(COMBOS))
    PADDING += int(PADDING/3)

    print("\n{}x{}x{} number of states is\n{:,}\n".format(size, size, size, COMBOS))

    #print("     {}  {}".format("This Depth".rjust(PADDING), "Total".rjust(PADDING)))
    #print("===  {}  {}".format("=" * PADDING, "=" * PADDING))
    #print("{:02d}:  {}  {}".format(1, "{:,}".format(prev_depth).rjust(PADDING), "{:,}".format(total).rjust(PADDING)))
    print("     {}".format("This Depth".rjust(PADDING)))
    print("===  {}".format("=" * PADDING))
    print("{:02d}:  {}".format(1, "{:,}".format(prev_depth).rjust(PADDING)))

    for depth in range(2, 100):
        this_depth = (MOVE_COUNT - 1) * prev_depth
        total += this_depth

        if total > COMBOS:
            over_by = total - COMBOS
            this_depth -= over_by
            total -= over_by

        #print("{:02d}:  {}  {}".format(depth, "{:,}".format(this_depth).rjust(PADDING), "{:,}".format(total).rjust(PADDING)))
        print("{:02d}:  {}".format(depth, "{:,}".format(this_depth).rjust(PADDING)))

        if total >= COMBOS:
            break

        prev_depth = this_depth

    print("\n")


def gods_number_333():
    gods_number(3, 18, 43252003274489856000)


def gods_number_444():
    gods_number(4, 36, 7401196841564901869874093974498574336000000000)


def gods_number_555():
    gods_number(5, 36, 282870942277741856536180333107150328293127731985672134721536000000)


if __name__ == "__main__":
    #gods_number_333()
    gods_number_444()
    #gods_number_555()
