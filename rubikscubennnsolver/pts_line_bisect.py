#!/usr/bin/env python2
# by pts@fazekas.hu at Fri Nov 29 19:20:15 CET 2013

""":" # Newline-separated file line bisection algorithms.

type -p python2.7 >/dev/null 2>&1 && exec python2.7 -- "$0" ${1+"$@"}
type -p python2.6 >/dev/null 2>&1 && exec python2.6 -- "$0" ${1+"$@"}
type -p python2.5 >/dev/null 2>&1 && exec python2.5 -- "$0" ${1+"$@"}
type -p python2.4 >/dev/null 2>&1 && exec python2.4 -- "$0" ${1+"$@"}
exec python -- "$0" ${1+"$@"}; exit 1

This is a Python 2.x module, it works with Python 2.4, 2.5, 2.6 and 2.7. It
was not probed with Python 3.x. Feel free to replace the #! line with
`#! /usr/bin/python', `#! /usr/bin/env python' or whatever suits you best.

License: GNU GPL v2 or newer, at your choice.

See http://pts.github.io/pts-line-bisect/line_bisect_evolution.html
for a detailed article about the design and analysis of the algorithms
implemented in this file.

This Python module can be used as a library or a script (see the main
function). The script is primarily for demo purposes. For production usage,
please use the C implementation instead in pts_lbsearch.c, which does less
IO (i.e. fewer calls to lseek(2) and read(2)), is faster, has more features
(i.e. more command-line flags).

TODO(pts): Add setup.py and upload to PyPi.
"""

import sys

def _read_and_compare(cache, ofs, f, size, tester):
    """
    Read a line from f at ofs, and test it.

    Finds out where the line starts, reads the line, calls tester with
    the line with newlines stripped, and returns the results.

    If ofs is in the middle of a line in f, then the following line will be
    used, otherwise the line starting at ofs will be used. (The term ``middle''
    includes the offset of the trailing '\\n'.)

    Bytes of f after offset `size' will be ignored. If a line spans over
    offset `size', it gets read fully (by f.readline()), and then truncated.

    If the line used starts at EOF (or at `size'), then tester won't be not
    called, and True is used instead.

    A cache of previous offsets and test results is read and updated. The size of
    the cache is bounded (it contains at most 4 offsets and 2 test results).

    Args:
      cache: A cache containing previous offsets and test results. It's a list
        of lists. An empty cache is the empty list, so initialize it to []
        before the first call. len(cache) is 0, 1, or 2. Each entry in cache is
        of the form [fofs, g, ofs].
      ofs: The offset in f to read from. If ofs is in the middle of a line, then
        the following line will be used.
      f: Seekable file object or file-like object to read from. The methods
        f.tell(), f.seek(ofs_arg) and f.readline() will be used.
      size: Size limit for reading. Bytes in f after offset `size' will be
        ignored.
      tester: Single-argument callable which will be called for the line, with
        the trailing '\\n' stripped. If the line used is at EOF, then tester
        won't be called and True will be used as the result.
    Returns:
      List or tuple of the form [fofs, g, dummy], where g is the test result
      (or True at EOF), fofs is the start offset of the line used in f,
      and dummy is an implementation detail that can be ignored.
    """
    # TODO(pts): Does increasing the cache size from 2 to 3 or 4 increase the hit
    # rate? Also document it in the article.
    #assert len(cache) <= 2
    #assert 0 <= ofs <= size

    if cache and cache[0][2] <= ofs <= cache[0][0]:
        cache.reverse()  # Move cache[0] to the end since we've just fetched it.

    elif len(cache) > 1 and cache[-1][2] <= ofs <= cache[-1][0]:
        pass  # We've found cache[-1] (same index as cache[1]).

    else:
        if ofs:
            if f.tell() != ofs - 1:  # Avoid lseek(2) call if not needed.
                f.seek(ofs - 1)  # Just to figure out where our line starts.
            f.readline()  # Ignore previous line, find our line.
            # Calling f.tell() is cheap, because Python remembers the lseek(2) retval.
            fofs = min(size, f.tell())
        else:
            fofs = 0

        #assert 0 <= ofs <= fofs <= size

        if cache and cache[0][0] == fofs:
            cache.reverse()  # Move cache[0] to the end since we've just fetched it.
            if cache[-1][2] > ofs:
                cache[-1][2] = ofs

        elif len(cache) > 1 and cache[-1][0] == fofs:
            if cache[-1][2] > ofs:
                cache[-1][2] = ofs
        else:
            g = True  # EOF is always larger than any line we search for.

            if fofs < size:

                if not fofs and f.tell():
                    f.seek(0)

                line = f.readline()  # We read at f.tell() == fofs.

                if f.tell() > size:
                    line = line[:size - fofs]

                if line:
                    g = tester(line.rstrip('\n'))

            if len(cache) > 1:  # Don't keep more than 2 items in the cache.
                del cache[0]
            cache.append([fofs, g, ofs])

    return cache[-1]  # Return the most recent item of the cache.


def bisect_way(f, x, is_left, size=None):
    """
    Return an offset where to insert line x into sorted file f.

    Bisection (binary search) on newline-separated, sorted file lines.
    If you use sort(1) to sort the file, run it as `LC_ALL=C sort' to make it
    lexicographically sorted, ignoring locale.

    If there is no trailing newline at the end of f, and the returned offset is
    at the end of f, then don't forget to append a '\\n' before appending x.

    Args:
      f: Seekable file object or file-like object to search in. The methods
        f.tell(), f.seek(ofs_arg) and f.readline() will be used.
      x: Line to search for. Must not contain '\\n', except for maybe a
        trailing one, which will be ignored if present.
      is_left: If true, emulate bisect_left. See the return value for more info.
      size: Size limit for reading. Bytes in f after offset `size' will be
        ignored. If None, then no limit.
    Returns:
      Byte offset in where where to insert line x. If is_left is true (i.e.
      bisect_left), then the smallest possible offset is returned, otherwise
      (i.e. bisect_right) the largest possible address is returned.
    """
    x = x.rstrip('\n')

    if is_left and not x:  # Shortcut.
        return 0

    if size is None:
        f.seek(0, 2)
        size = f.tell()

    if size <= 0:  # Shortcut.
        return 0

    if is_left:
        tester = x.__le__  # x <= y.
    else:
        tester = x.__lt__  # x < y.

    lo, hi, mid, cache = 0, size - 1, 1, []

    while lo < hi:
        mid = (lo + hi) >> 1
        midf, g, _ = _read_and_compare(cache, mid, f, size, tester)
        if g:
            hi = mid
        else:
            lo = mid + 1

    if mid != lo:
        midf = _read_and_compare(cache, lo, f, size, tester)[0]

    return midf


def bisect_right(f, x, size=None):
    """
    Return the largest offset where to insert line x into sorted file f.

    Similar to bisect.bisect_right, but operates on lines rather then elements.
    Convenience function which just calls bisect_way(..., is_left=False).
    """
    return bisect_way(f, x, False, size)


def bisect_left(f, x, size=None):
    """
    Return the smallest offset where to insert line x into sorted file f.

    Similar to bisect.bisect_left, but operates on lines rather then elements.
    Convenience function which just calls bisect_way(..., is_left=True).
    """
    return bisect_way(f, x, True, size)


def bisect_interval(f, x, y=None, is_open=False, size=None):
    """
    Return (start, end) offset pair for lines between x and y.

    Args:
      f: Seekable file object or file-like object to search in. The methods
        f.tell(), f.seek(ofs_arg) and f.readline() will be used.
      x: First line to search for. Must not contain '\\n', except for maybe a
        trailing one, which will be ignored if present.
      y: First line to search for. Must not contain '\\n', except for maybe a
        trailing one, which will be ignored if present. If None, x is used.
      is_open: If true, then the returned interval consists of lines
        x <= line < y. Otherwise it consists of lines x <= line <= y.
      size: Size limit for reading. Bytes in f after offset `size' will be
        ignored. If None, then no limit.
    Returns:
      Return (start, end) offset pair containing lines between x and y (see
      arg is_open whether x and y are inclusive) in sorted file f, before offset
      `size'. These offsets contain the lines: start <= ofs < end. Trailing
      '\\n's are included in the interval (except at EOF if there was none).
    """
    x = x.rstrip('\n')

    if y is None:
        y = x
    else:
        y = y.strip('\n')

    end = bisect_way(f, y, is_open, size)

    if is_open and x == y:
        return end, end
    else:
        return bisect_way(f, x, True, end), end


def get_line_startswith(f, target_line):
    start = bisect_way(f, target_line, True, None)

    # start = bisect_way(f, x, True, end), end
    # (start, end) = bisect_interval(f, line, line, True)

    if start is not None:
        f.seek(start)
        line = f.readline()

        if line.startswith(target_line):
            return line

    return None


if __name__ == '__main__':
    """
    Command-line tool for binary search in a line-sorted text file.

    Command-line is a subset of pts_lbsearch.c. We are a bit slower, because
    we seek more.

    For production usage, please use the C implementation instead in
    pts_lbsearch.c, which does less IO (i.e. fewer calls to lseek(2) and
    read(2)), is faster, has more features (i.e. more command-line flags).
    """
    argv = sys.argv

    def usage_error(msg):
        sys.stderr.write(
            'Binary search (bisection) in a sorted text file\n'
            'Usage: %s -<flags> <sorted-text-file> <key-x> <key-y>\n'
            '<key-x> is the first key to search for\n'
            '<key-y> is the last key to search for; default is <key-x>\n'
            'Flags:\n'
            'e: do bisect_left, open interval end\n'
            't: do bisect_right, closed interval end\n'
            'b: do bisect_left for interval start (default)\n'
            'a: do bisect_right for interval start (for append position)\n'
            'c: print file contents (default)\n'
            'o: print file offsets\n'
            'usage error: %s\n' % (argv[0], msg))
        sys.exit(1)

    if len(argv) not in (4, 5):
        usage_error('incorrect argument count')

    if not argv[1].startswith('-'):
        usage_error('missing flags')

    filename = argv[2]
    x = argv[3].rstrip('\n')

    if len(argv) > 4:
        y = argv[4].rstrip('\n')
    else:
        y = x

    is_open = None
    is_leftstart = True
    do_print_contents = True

    for flag in argv[1][1:]:
        if flag == 'e':
            is_open = True
        elif flag == 't':
            is_open = False
        elif flag == 'b':
            is_leftstart = True
        elif flag == 'a':
            is_leftstart = False
        elif flag == 'c':
            do_print_contents = True
        elif flag == 'o':
            do_print_contents = False
        else:
            usage_error('unsupported flag')

    is_open = True
    do_print_contents = True

    if is_open is None:
        usage_error('missing boundary flag')

    if not is_leftstart and not (is_open and not do_print_contents and y is None):
        usage_error('flag -a needs -eo and no <key-y>')

    if is_open and do_print_contents and y is None:
        usage_error('single-key contents is always empty')

    with open(filename, 'r') as f:
        if is_open and not do_print_contents and y is None:
            sys.stdout.write('%d\n' % bisect_way(f, x, is_leftstart))
        else:
            start, end = bisect_interval(f, x, y, is_open)

            if do_print_contents:
                # Similar to: f.rewind(); sys.stdout.write(f.read()[start : end])
                f.seek(start)
                line = f.readline()
                sys.stdout.write(line)

                '''
                remaining = end - start
                while remaining > 0:
                    data = f.read(min(remaining, 65536))
                    if not data:
                        break
                    sys.stdout.write(data)
                    remaining -= len(data)
                '''
            else:
                sys.stdout.write('%d %s\n' % (start, end))

            if start >= end:
                sys.exit(3)
