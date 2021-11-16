from math import sqrt,log
import random

__all__ = [
    'gcd', 'lcm',
    'primes_to', 'not_primes_to',
    'factor', 'divisors', 'proper_divisors',
    'is_abundant', 'is_amicable', 'is_deficient', 'is_perfect',
    'is_probably_prime', 'next_probably_prime', 'powmod', 'mult_inverse']


def gcd(a, b):
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
    return a*b/gcd(a, b)


def powmod(n, e, m):
    """Return (n**e) % m"""
    a = 1
    while e:
        if e%2 == 1:
            a *= n
            a %= m
        e //= 2
        n *= n
        n %= m
    return a


def __add_prime():
    __primes = __add_prime.__primes
    n = __primes[-1] + 2
    while True:
        # test if n is prime
        sn = int(sqrt(n))
        for p in __primes:
            if p > sn:
                __primes.append(n)
                return
            if n%p == 0:
                n += 2
                break
        else:
            __primes.append(n)
            return
__add_prime.__primes = [2, 3]


def primes_to(limit):
    """
    An iterator that produces all prime numbers (p) in ascending order that 1 < p <= limit

    :param limit: The largest prime to return
    :return: An iterator over primes
    """
    __primes = __add_prime.__primes
    i = 0
    p = __primes[i]
    while p <= limit:
        yield p
        i += 1
        if len(__primes) <= i:
            __add_prime()
        p = __primes[i]


def not_primes_to(limit):
    """
    An iterator that produces all non-prime numbers (n) in ascending order s.t. 1 <= n <= limit

    :param limit: The largest prime to return
    :return: An iterator over primes
    """
    __primes = __add_prime.__primes
    i = 0
    l = 1
    p = __primes[i]
    while p <= limit:
        while l < p:
            yield l
            l += 1
        l = p + 1
        i += 1
        if len(__primes) <= i:
            __add_prime()
        p = __primes[i]


def factor(n):
    """
    Factor a number into its prime components

    :return: A list of tuples of (count, prime factor)"""
    __primes = __add_prime.__primes
    limit = int(sqrt(n))
    factors = []
    i = 0
    p = 2
    while p <= limit:
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        if c:
            limit = int(sqrt(n))
            factors.append((c, p))
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

    :param n: The input
    :return: A list of integers
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

    :param n: The input
    :return: A list of integers
    """
    return divisors(n)[:-1]


def sum_proper_divisors(n):
    spds = sum_proper_divisors.sum_divisors
    if n in spds:
        return spds[n]
    spd = sum(proper_divisors(n))
    spds[n] = spd
    return spd
sum_proper_divisors.sum_divisors = {}


def is_amicable(n):
    spd = sum_proper_divisors(n)
    return spd != n and sum_proper_divisors(spd) == n


def is_perfect(n):
    return n == sum_proper_divisors(n)


def is_deficient(n):
    return n > sum_proper_divisors(n)


def is_abundant(n):
    return n < sum_proper_divisors(n)


def is_probably_prime(n):
    up_to = 257
    if up_to >= n:
        up_to = n // 2
    # quick scan to weed out many values
    for a in primes_to(up_to):
        if n%a == 0:
            return False

    # Miller-Rabin primality test, always correct up limits shown, 3x10**24
    d = n-1
    r = 0
    while (d & 1) == 0:
        d //= 2
        r += 1

    if n < 3215031751:
        up_to = 7
    elif n < 341550071728321:
        up_to = 17
    elif n < 3825123056546413051:
        up_to = 23
    elif n < 3317044064679887385961981:
        up_to = 41
    else:
        up_to = 47
    for a in primes_to(up_to):
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
    while not is_probably_prime(n):
        n += 2
    return n

def mult_inverse(a, n):
    """returns 0 if there is no inverse"""
    t1 = 0
    t2 = 1
    r1 = n
    r2 = a

    while r2 != 0:
        quotient = r1 // r2

        t3 = t1 - quotient * t2
        t1 = t2
        t2 = t3

        r3 = r1 - quotient * r2
        r1 = r2
        r2 = r3

    if r1 > 1:
        return 0
    if t1 < 0:
        t1 = t1 + n

    return t1

if __name__ == '__main__':
    print(is_probably_prime(3317044064679887385961981))

