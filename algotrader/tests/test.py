# from collections import OrderedDict
# import pandas as pd
#
# d = OrderedDict()
#
# d["test"] = 1
# d["bar"] = 2
# d["foo"] = 3
# d["foo"] = 4
# d["foo2"] = 5
#
# print d
#
# print len(d)
#
# s = pd.Series(d, name='Value')
# s.index.name = 'Time'
#
# print s
#
# print d.items()[-1][1]


import concurrent.futures
import math

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419]

def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print('%d is prime: %s' % (number, prime))

if __name__ == '__main__':
    main()