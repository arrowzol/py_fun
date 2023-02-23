from math import sqrt,log
from secrets import randbelow
from functools import reduce
from bisect import bisect_left, bisect_right
from bitmap import BitMap

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
PCL = 500*1000*1000

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


__primes = []

def __sieve_Eratosthenes(upto):
    """
    most efficient for primes up to 100M
    """
    global __primes

    # bootstrap up to first odd prime
    if not __primes:
        __primes.append(2)
        __primes.append(3)

    # if we've already got it, bail
    last_prime = __primes[-1]
    if last_prime >= upto:
        return

    # at least double the range
    if upto < last_prime*2:
        upto = last_prime*2

    # but not more than PCL
    if upto > PCL:
        upto = PCL

    limit = int(sqrt(upto))+1
    bm = BitMap(upto//2)

    # sieve in known primes
    for p in __primes:
        if p != 2:
            start = 3*p
            if start < last_prime:
                start += (2*p)*((2*p - 1 + last_prime - start)//(2*p))
            for pm in range(start, upto, 2*p):
                bm.set(pm//2)

    # sieve in new primes
    for i in range(last_prime+2, limit, 2):
        if not bm.test(i//2):
            __primes.append(i)
            for pm in range(3*i, upto, 2*i):
                bm.set(pm//2)

    # record primes larger that sqrt(upto)
    last_prime = __primes[-1]
    for j in range(last_prime+2, upto, 2):
        if not bm.test(j//2):
            __primes.append(j)

    # add one more, some of the algos expect this
    last_prime = __primes[-1]
    __primes.append(next_probably_prime(last_prime))

def random_prime_to(limit):
    """
    Return one prime (p) with 1 < p <= limit.
    Each prime between 1 and limit has the same chance to be returned.
    The ransomness is cryptographically random.
    """
    global __primes

    if limit > PCL:
        raise Exception("this limit is not supported")

    __sieve_Eratosthenes(limit)
    i = bisect_right(__primes, limit)
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

    __sieve_Eratosthenes(limit)
    i = 0
    p = __primes[i]
    while p <= limit:
        yield p
        if p < PCL:
            i += 1
            p = __primes[i]
        else:
            p += 2
            while not probably_prime(p):
                p += 2


def not_primes_to(limit):
    """
    An iterator that produces all non-prime numbers (n) in ascending order where 1 <= n <= limit
    note that identifying primes becomes increasingly CPU intensive as they get larger
    answers are cached to avoid recomputing on subsequent calls

    :param limit: The largest prime to return
    :return: An iterator over primes
    """
    global __primes

    __sieve_Eratosthenes(limit)
    i = 0
    np = 1
    p = __primes[i]
    while p <= limit:
        while np < p:
            yield np
            np += 1
        np = p + 1
        if p < PCL:
            i += 1
            p = __primes[i]
        else:
            p += 2
            while not probably_prime(p):
                p += 2
    while np <= limit:
        yield np
        np += 1


def factor(n, upto=0):
    """
    Factor a number into its prime components
    note that this becomes increasingly CPU intensive as the largest factor of n becomes larger

    :return: A list of tuples of (count, prime factor)
    """
    global __primes

    limit = int(sqrt(n))+1
    __sieve_Eratosthenes(limit)
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
            limit = int(sqrt(n))+1
        if p < PCL:
            i += 1
            p = __primes[i]
        else:
            p += 2
            while not probably_prime(p):
                p += 2
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
        upto = int(sqrt(n))+1
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
    elif n < 170584961:
        a_list = [350, 3958281543]
    elif n < 4759123141:
        a_list = [2, 7, 61]
    elif n < 75792980677:
        a_list = [2, 379215, 457083754]
#   elif n < 118670087467:
#       if n == 3215031751:
#           return False
#       upto = 7
#   elif n < 2152302898747:
#       upto = 11
#   elif n < 3474749660383:
#       upto = 13
    elif n < 21652684502221:
        a_list = [2, 1215, 34862, 574237825]
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

__sieve_Eratosthenes(1000*1000)

if __name__ == '__main__':
    if False:
        p = 23
        for i in range(1, p):
            print("multiplicative inverse of %d mod %d = %d"%(i, p, mult_inverse(i, p)))

    if False:
        PCL = 1800*1000
        p_sum = 0
        for p in primes_to(2*1000*1000):
            p_sum += p
        print("sum of primes to 2M: %d"%p_sum)
        if p_sum != 142913828922:
            raise Exception("prime list incorrect")

        np_sum = 0
        for np in not_primes_to(2*1000*1000):
            np_sum += np
        print("sum of non-primes to 2M: %d"%np_sum)
        if np_sum != 1857087171078:
            raise Exception("non-prime list incorrect")

        if __primes[-1] != 1800037:
            raise Exception("too many primes cached")

        PCL = 20*1000*1000

    if True:
        PCL = 300*1000*1000
        p_sum = 0
        for p in primes_to(300*1000*1000):
            p_sum += p
        print("sum of primes to 2M: %d"%p_sum)

