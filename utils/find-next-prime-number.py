#!/usr/bin/env python

import sys

def find_next_prime(n):
    return find_prime_in_range(n, 2*n)

def find_prime_in_range(a, b):
    for p in range(a, b):
        for i in range(2, p):
            if p % i == 0:
                break
        else:
            return p
    return None

if __name__ == '__main__':
    print(find_next_prime(int(sys.argv[1])))
