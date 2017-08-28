from math import sqrt

__all__ = [
    'gcd', 'lcm',
    'primes_to', 'not_primes_to',
    'factor', 'divisors', 'proper_divisors',
    'is_abundant', 'is_amicable', 'is_deficient', 'is_perfect',
    'is_probably_prime', 'next_probably_prime', 'powmod']


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
            n /= p
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
    # Quickly trim search with Fermat's test using a=2
    if powmod(2, n-1, n) != 1:
        return False
    # Fermat's test using a=2 fails starting at 341
    if n < 341:
        return True
        
    # Now try more robust, but more expensive Miller-Rabin test
    nm1 = n-1
    d = nm1
    s = 1
    while d % 2 == 0:
        d /= 2
        s *= 2
    for a in primes_to(100):
        if powmod(a, d, n) != 1:
            ss = 1
            found = False
            while ss < s:
                if powmod(a, ss*d, n) == nm1:
                    found = True
                    break
                ss *= 2
            if not found:
                return False
    return True


def next_probably_prime(n):
    if n%2 == 0:
        n += 1
    while not is_probably_prime(n):
        n += 2
    return n
