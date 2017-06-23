#!/usr/bin/env python2

import datetime as dt
import logging
import sys
from rubikscubennnsolver.LookupTable import LookupTable
from rubikscubennnsolver.RubiksCube555 import moves_5x5x5, RubiksCube555

# lookup-table-5x5x5-step10-UD-centers-stage.txt.7-deep is 5.9G and 328,877,780 lines
# It takes us 6.5s to locate 421,404 entries with an avg left/right of 4825
#
# It turns out a bunch of those 421,404 entries were dups, I fixed that and some
# other minor tweaks and got it down to 3.8s with avg left/right of 9796

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)17s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)


# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))


cube = RubiksCube555('DFFURRULDLDLURLBDDRRBFRURFBFBFRBDLBBFRBLRFBRBBFLULDLBLULLFRUBUFLDFFLDULDDLUURRDRFBRLULUDRBDUUUBBRFFDBDFURDBBDDRULBUDRDLLLBDRFDLRDLLFDBBUFBRURFFUFFUUFU')

lt = LookupTable(cube,
                 '../lookup-table-5x5x5-step10-UD-centers-stage.txt',
                 'UD-centers-stage',
                 '3fe000000001ff',
                 True,
                 moves_5x5x5)


# should not find this one
with open(lt.filename, 'r') as fh:
    print(lt.file_binary_search(fh, '0206f462228611'))

# should find this one
with open(lt.filename, 'r') as fh:
    print(lt.file_binary_search(fh, '3ffec000100012'))


states_to_find = []
with open('states-to-find-lookup-table-5x5x5-step10-UD-centers-stage.txt', 'r') as fh:
    for line in fh:
        states_to_find.append(line.strip())

'''
start_time = dt.datetime.now()
log.info("python one by one start")
with open(lt.filename, 'r') as fh:
    lt.file_binary_search_multiple_keys_one_by_one_python(fh, states_to_find)
end_time = dt.datetime.now()
log.info("python one by one - took %s" % (end_time - start_time))
log.info("file_binary_search_guts called %d time with an average range of %s" %
    (lt.guts_call_count, int(lt.guts_left_right_range/lt.guts_call_count)))
'''

'''
start_time = dt.datetime.now()
log.info("python low high start")
with open(lt.filename, 'r') as fh:
    results = lt.file_binary_search_multiple_keys_low_high_python(fh, states_to_find)
end_time = dt.datetime.now()
log.info("python low high end - took %s" % (end_time - start_time))
log.info("file_binary_search_guts called %d time with an average range of %s" %
    (lt.guts_call_count, int(lt.guts_left_right_range/lt.guts_call_count)))

with open('low_high.txt', 'w') as fh:
    for key in sorted(results.keys()):
        fh.write("%s:%s\n" % (key, results[key]))
'''


'''
start_time = dt.datetime.now()
log.info("C low high start")
with open(lt.filename, 'r') as fh:
    lt.file_binary_search_multiple_keys_low_high_C(fh, states_to_find)
end_time = dt.datetime.now()
log.info("C low high end - took %s" % (end_time - start_time))

'''


start_time = dt.datetime.now()
log.info("python low low start")
with open(lt.filename, 'r') as fh:
    results = lt.file_binary_search_multiple_keys_low_low_python(fh, states_to_find)
end_time = dt.datetime.now()
log.info("python low low end - took %s" % (end_time - start_time))
log.info("file_binary_search_guts called %d time with an average range of %s, %d fh.seek() calls, %d lines read" %
    (lt.guts_call_count, int(lt.guts_left_right_range/lt.guts_call_count), lt.fh_seek_call_count, lt.fh_seek_lines_read))

#with open('low_low.txt', 'w') as fh:
#    for key in sorted(results.keys()):
#        fh.write("%s:%s\n" % (key, results[key]))
