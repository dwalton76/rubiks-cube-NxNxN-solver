#!/usr/bin/env python3

from bloomfilter import BloomFilter
from random import shuffle

# words to be added
word_present = ['abound','abounds','abundance','abundant','accessable',
                'bloom','blossom','bolster','bonny','bonus','bonuses',
                'coherent','cohesive','colorful','comely','comfort',
                'gems','generosity','generous','generously','genial']

# word not added
word_absent = ['bluff','cheater','hate','war','humanity',
               'racism','hurt','nuke','gloomy','facebook',
               'geeksforgeeks','twitter']


n = len(word_present) # no of items to add
n = 4096
p = 0.10 # false positive probability

bloomf = BloomFilter(n, p)
print("")
print("Size of bit array          : %d" % bloomf.size)
print("False positive Probability : %s" % bloomf.fp_prob)
print("Number of hash functions   : %s" % bloomf.hash_count)

#for item in word_present:
#    bloomf.add(item)

bloomf.load_bit_array()
#shuffle(word_present)
#shuffle(word_absent)

test_words = word_present[:10] + word_absent
#shuffle(test_words)
print("")

for word in test_words:
    if bloomf.check(word):
        if word in word_absent:
            print("%-20s YES (false positive)" % word)
        else:
            print("%-20s YES" % word)
    else:
        print("%-20s NO" % word)

print("")

bloomf.save_bit_array()
