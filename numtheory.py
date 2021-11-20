from math import sqrt,log
from secrets import randbelow
from functools import reduce
from bisect import bisect_left

__all__ = [
    # exponentiation
    'power', 'powmod', 'mult_inverse',

    # raw prime numbers
    'primes_to', 'not_primes_to', 'random_prime_to',
    'probably_prime', 'next_probably_prime',

    # factoring and friends
    'factor', 'divisors', 'proper_divisors',
    'gcd', 'lcm',
    'carmichael_lambda', 'carmichael_lambda_list'

    # curiosities
    'is_abundant', 'is_amicable', 'is_deficient', 'is_perfect',
    ]

# Prime Cache Limit
PCL = 1000000

def gcd(a, b):
    """
    Compute greatest common divisor of a and b
    inputs may be large integers

    :param a: input value
    :param b: input value
    :return: gcd(a,b)
    """
    if a < 0:
        a = -a
    if b < 0:
        b = -b
    if a > b:
        tmp = a
        a = b
        b = tmp
    while True:
        if a == 0:
            return b
        b %= a
        if b == 0:
            return a
        a %= b


def lcm(a, b):
    """
    Compute least common multiple of a and b
    inputs may be large integers

    :param a: input value
    :param b: input value
    :return: lcm(a,b)
    """
    return a*b//gcd(a, b)


def power(n, e):
    """
    Compute n^e

    :param n: input value
    :param e: input value
    :return: n^e
    """
    a = 1
    while e:
        if e&1 == 1:
            a *= n
        e >>= 1
        n *= n
    return a


def powmod(n, e, m):
    """
    Compute (n^e) mod m
    inputs may be large integers

    :param n: input value
    :param e: input value
    :param m: input value
    :return: n^e mod m
    """
    a = 1
    while e:
        if e&1 == 1:
            a *= n
            a %= m
        e >>= 1
        n *= n
        n %= m
    return a


__primes = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def __add_prime():
    global __primes

    n = __primes[-1] + 2
    while not probably_prime(n):
        n += 2
    __primes.append(n)


def random_prime_to(limit):
    global __primes

    if limit > PCL:
        raise Exception("this limit is not supported")

    while __primes[-1] < limit:
        __add_prime()

    i = bisect_left(__primes, limit)
    if __primes[i] < limit:
        limit += 1
    return __primes[randbelow(i)]

def primes_to(limit):
    """
    An iterator that produces all prime numbers (p) in ascending order that 1 < p <= limit
    note that identifying primes becomes increasingly CPU intensive as they get larger
    answers are cached to avoid recomputing on subsequent calls

    :param limit: The largest prime to return
    :return: An iterator over primes
    """
    global __primes

    i = 0
    p = __primes[i]
    while p <= limit:
        yield p
        if p < PCL:
            i += 1
            if len(__primes) <= i:
                __add_prime()
            p = __primes[i]
        else:
            p += 2
            while not probably_prime(p):
                p += 2


def not_primes_to(limit):
    """
    An iterator that produces all non-prime numbers (n) in ascending order s.t. 1 <= n <= limit
    note that identifying primes becomes increasingly CPU intensive as they get larger
    answers are cached to avoid recomputing on subsequent calls

    :param limit: The largest prime to return
    :return: An iterator over primes
    """
    global __primes

    i = 0
    l = 1
    p = __primes[i]
    while p <= limit:
        while l < p:
            yield l
            l += 1
        l = p + 1
        i += 1
        if p < PCL:
            if len(__primes) <= i:
                __add_prime()
            p = __primes[i]
        else:
            p += 2
            while not probably_prime(p):
                p += 2


def factor(n, upto=0):
    """
    Factor a number into its prime components
    note that this becomes increasingly CPU intensive as the largest factor of n becomes larger

    :return: A list of tuples of (count, prime factor)
    """
    global __primes

    limit = int(sqrt(n))
    factors = []
    i = 0
    p = 2
    while p <= limit and (not upto or p < upto):
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        if c:
            factors.append((c, p))
            if probably_prime(n):
                break
            limit = int(sqrt(n))
        i += 1
        if len(__primes) <= i:
            __add_prime()
        p = __primes[i]
    if n > 1:
        factors.append((1, n))
    return factors


def divisors(n):
    """
    Calculate all the positive divisors of n
    note that this becomes increasingly CPU intensive as the largest factor of n becomes larger

    :param n: input value
    :return: list of divisors of n
    """
    f = factor(n)
    l = []
    stop = len(f)

    def add(a, i):
        if i == stop:
            l.append(a)
        else:
            c, p = f[i]
            while c >= 0:
                c -= 1
                add(a, i+1)
                a *= p
    add(1, 0)
    return l


def proper_divisors(n):
    """
    Calculate all the proper divisors of n
    note that this becomes increasingly CPU intensive as the largest factor of n becomes larger

    :param n: The input
    :return: A list of integers
    """
    return divisors(n)[:-1]


def sum_proper_divisors(n):
    """
    """
    spds = sum_proper_divisors.sum_divisors
    if n in spds:
        return spds[n]
    spd = sum(proper_divisors(n))
    spds[n] = spd
    return spd
sum_proper_divisors.sum_divisors = {}


def is_amicable(n):
    """
    Detect amicable numbers, number which
    """
    spd = sum_proper_divisors(n)
    return spd != n and sum_proper_divisors(spd) == n


def is_perfect(n):
    """
    Detect perfect numbers, number where sum(proper divisors of n) = n

    :param n: The input
    :return: True if n is perfect
    """
    return n == sum_proper_divisors(n)


def is_deficient(n):
    """
    Detect perfect numbers, number where sum(proper divisors of n) = n

    :param n: The input
    :return: True if n is perfect
    """
    return n > sum_proper_divisors(n)


def is_abundant(n):
    """
    Detect perfect numbers, number where sum(proper divisors of n) = n

    :param n: The input
    :return: True if n is perfect
    """
    return n < sum_proper_divisors(n)


def probably_prime(n):
    """
    Test any number for primality
    Guaranteed accurate up to 3,317,044,064,679,887,385,961,981 or about 3x10**24

    note: values taken from https://primes.utm.edu/prove/prove2_3.html
    """
    if n < 2:
        return False

    # quick scan to weed out many values
    upto = 53
    if upto*upto >= n:
        upto = int(sqrt(n))
    for a in primes_to(upto):
        if n%a == 0:
            return False

    # choose list of values for Miller-Rabin test
    a_list = None
    if   n < 53*53:
        return True
    elif n < 1373653:
        upto = 3
    elif n < 9080191:
        a_list = [31, 73]
    elif n < 4759123141:
        a_list = [2, 7, 61]
    elif n < 2152302898747:
        upto = 11
    elif n < 3474749660383:
        upto = 13
    elif n < 341550071728321:
        upto = 17
    elif n < 3825123056546413051:
        upto = 23
    elif n < 3317044064679887385961981:
        upto = 41
    else:
        # this is where the "probably" prime kicks in
        upto = 47

    if not a_list:
        a_list = primes_to(upto)

    # Miller-Rabin primality test, always correct up limits shown
    d = n-1
    r = 0
    while (d & 1) == 0:
        d >>= 1
        r += 1

    for a in a_list:
        x = powmod(a, d, n)
        if x != 1 and x != n-1:
            for y in range(r-1):
                x = (x*x) % n
                if x == n-1:
                    break
            else:
                return False
    return True


def next_probably_prime(n):
    n += 1 + (n&1)
    while not probably_prime(n):
        n += 2
    return n

def mult_inverse(a, n):
    """returns 0 if there is no inverse"""
    t1 = 0
    t2 = 1
    r1 = n
    r2 = a

    while r2 != 0:
        q = r1 // r2

        t3 = t1 - q * t2
        t1 = t2
        t2 = t3

        r3 = r1 - q * r2
        r1 = r2
        r2 = r3

    if r1 > 1:
        return 0
    if t1 < 0:
        t1 = t1 + n

    return t1

def euler_phi(n):
    phi = 1
    for c, p in factor(n):
        phi *= (p-1)*power(p, c-1)
    return phi

def carmichael_lambda(n):
    p2c = {}
    for c, p in factor(n):
        # carmichael lambda of prime^exponent
        if p == 2 and c >= 3:
            lamb = (p-1)*power(p, c-2)
        else:
            lamb = (p-1)*power(p, c-1)

        # perform lcm by finding max(exponents) for each prime
        for c,p in factor(lamb):
            p2c[p] = max(p2c.get(p,0), c)
    return reduce(
        lambda x,y:x*y,
        (power(p,c) for p,c in p2c.items()),
        1)

def carmichael_lambda_list(ns):
    p2c = {}
    for n in ns:
        for c, p in factor(n):
            # carmichael lambda of prime^exponent
            if p == 2 and c >= 3:
                lamb = (p-1)*power(p, c-2)
            else:
                lamb = (p-1)*power(p, c-1)

            # perform lcm by finding max(exponents) for each prime
            for c,p in factor(lamb):
                p2c[p] = max(p2c.get(p,0), c)
    return reduce(
        lambda x,y:x*y,
        (power(p,c) for p,c in p2c.items()),
        1)

if __name__ == '__main__':
#    p = 23
#    for i in range(1, p):
#        print("multiplicative inverse of %d mod %d = %d"%(i, p, mult_inverse(i, p)))

    p_sum = 0
    for p in primes_to(2000000):
        p_sum += p
    print("sum of primes to 2M: %d"%p_sum)
    if p_sum != 142913828922:
        raise Exception("prime list incorrect")

    np_sum = 0
    for np in not_primes_to(2000000):
        np_sum += np
    print("sum of non-primes to 2M: %d"%np_sum)
    if np_sum != 1857073171099:
        raise Exception("non-prime list incorrect")

