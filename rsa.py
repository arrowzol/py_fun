import numtheory as nt
import secrets

__all__ = [
    'Key',
    'create_key_from_primes', 'create_key_bits',
    'encrypt_raw', 'decrypt_raw'
    'encrypt_pkcs1', 'decrypt_pkcs1'
    ]

class Key:
    def __init__(self, n, e, d, phi, primes):
        self.n = n
        self.e = e
        self.d = d
        self.phi = phi
        self.primes = primes

def create_key_from_primes(primes, e):
    n = phi = 1
    for p in primes:
        n *= p
        phi *= (p-1)
    while True:
        d = nt.mult_inverse(e, phi)
        if d != 0:
            break
        e += 1
    return Key(n, e, d, phi, primes)

def random_prime(bits):
    if bits <= 2:
        return 2
    if bits <= 3:
        return 3
    n = secrets.randbits(bits-1) | (1 << bits) | 1
    while not nt.probably_prime(n):
        n += 2
    return n

def create_key_bits(bits, r_count=2, e=None):
    if not e:
        if bits >= 14:
            e = 0x1001
        elif bits >= 10:
            e = 0x101
        else:
            e = 0x11
    bits += 1
    primes = []
    n = 1
    for r in range(r_count):
        p_bits = (bits - n.bit_length()) // (r_count - r)
        p = random_prime(p_bits)
        p |= 1 << p_bits
        while p in primes:
            p = nt.next_probably_prime(p)
        n *= p
        primes.append(p)
    if bits > 10 and n.bit_length() > bits:
        p = p >> 1
        p |= 1
        while not nt.probably_prime(p):
            p += 2
        primes[-1] = p
    return create_key_from_primes(primes, e)

def encrypt_raw(key, m):
    return nt.powmod(m, key.e, key.n)

def encrypt_pkcs1(key, m):
    k = key.n.bit_length()-1
    data_bits = k - 11*8
    padding_offset = data_bits + 1*8
    cmd_offset = data_bits + 9*8

    raw_m =  (2 << cmd_offset) | (secrets.randbits(8*8) << padding_offset) | m
    return nt.powmod(raw_m, key.e, key.n)

def decrypt_raw(key, c):
    return nt.powmod(c, key.d, key.n)

def decrypt_pkcs1(key, c):
    raw_m = nt.powmod(c, key.d, key.n)

    k = key.n.bit_length()-1
    data_bits = k - 11*8
    padding_offset = data_bits + 1*8
    cmd_offset = data_bits + 9*8

    cmd = raw_m >> cmd_offset
    if cmd != 2:
        return 0
    data = raw_m & ((1 << data_bits) - 1)
    return data


if __name__ == '__main__':
    import sys

    bits = 100
    if len(sys.argv) >= 2:
        bits = int(sys.argv[1])

    key = create_key_bits(bits)
    print("n=0x{0:x} e=0x{1:x} d=0x{2:x}".format(key.n, key.e, key.d))

    print("RAW")
    for m in range(2, 10):
        c = encrypt_raw(key, m)
        m2 = decrypt_raw(key, c)
        print("{0} -> {0}   0x{2:x}".format(m, m2, c))

    print("PKCS1")
    for m in range(2, 10):
        c = encrypt_pkcs1(key, m)
        m2 = decrypt_pkcs1(key, c)
        print("{0} -> {0}   0x{2:x}".format(m, m2, c))

