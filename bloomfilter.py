# Python 3 program to build Bloom Filter

import logging
import math
import sys
from bitarray import bitarray
from pprint import pformat
import pickle

# pip install mmh3
import mmh3 # MurmurHash3

log = logging.getLogger(__name__)


class BloomFilter(object):
    """
    Class for Bloom filter, using murmur3 hash function

    https://www.geeksforgeeks.org/bloom-filters-introduction-and-python-implementation/
    """

    def __init__(self, items_count, fp_prob, filename):
        """
        items_count : int
            Number of items expected to be stored in bloom filter
        fp_prob : float
            False Positive probability in decimal
        """
        # False posible probability in decimal
        self.fp_prob = fp_prob

        # Size of bit array to use
        self.size = self.get_size(items_count, fp_prob)

        # number of hash functions to use
        self.hash_count = self.get_hash_count(self.size, items_count)

        # Bit array of given size
        self.bit_array = bitarray(self.size)

        # initialize all bits as 0
        self.bit_array.setall(0)

        self.filename = filename
        self.filename_bf = filename + '.bf'

    def __str__(self):
        return self.filename

    def add(self, item):
        """
        Add an item in the filter
        """
        digests = []
        for i in range(self.hash_count):

            # create digest for given item.
            # i work as seed to mmh3.hash() function
            # With different seed, digest created is different
            digest = mmh3.hash(item,i) % self.size
            digests.append(digest)

            # set the bit True in bit_array
            self.bit_array[digest] = 1

    def check(self, item):
        """
        Check for existence of an item in filter
        """
        log.info("%s: check start for %s" % (self, item))
        for i in range(self.hash_count):
            digest = mmh3.hash(item,i) % self.size

            if not self.bit_array[digest]:

                # if any of bit is False then,its not present
                # in filter
                # else there is probability that it exist
                return False
        log.info("%s: check end for %s" % (self, item))
        # dwalton
        import sys
        sys.exit(0)
        return True

    def get_size(self,n,p):
        """
        Return the size of bit array(m) to used using
        following formula
        m = -(n * lg(p)) / (lg(2)^2)
        n : int
            number of items expected to be stored in filter
        p : float
            False Positive probability in decimal
        """
        m = -(n * math.log(p))/(math.log(2)**2)
        return int(m)

    def get_hash_count(self, m, n):
        """
        Return the hash function(k) to be used using
        following formula
        k = (m/n) * lg(2)

        m : int
            size of bit array
        n : int
            number of items expected to be stored in filter
        """
        k = (m/n) * math.log(2)
        return int(k)

    def save_bit_array(self):
        with open(self.filename_bf, 'w') as fh:
            for x in self.bit_array:
                fh.write(str(x))
            fh.write('\n')

    def load_bit_array(self):
        with open(self.filename_bf, 'r') as fh:
            line = next(fh)
            line = line.strip()
            self.bit_array = list(map(int, line))


class BloomFilterFromFile(BloomFilter):

    def __init__(self, items_count, filename):
        self.filename = filename
        self.filename_bf = filename + '.bf'

        log.info("%s: load bit_array start" % self)
        with open(self.filename_bf, 'r') as fh:
            line = next(fh)
            line = line.strip()
            self.bit_array = list(map(int, line))
        log.info("%s: load bit_array end" % self)

        # Size of bit array to use
        self.size = len(self.bit_array)

        # number of hash functions to use
        self.hash_count = self.get_hash_count(self.size, items_count)
        log.info("%s: hash_count %d" % (self, self.hash_count))
