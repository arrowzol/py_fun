import numtheory as nt
import random

__all__ = [
    'create_key_from_primes', 'create_key_bits',
    'encrypt_raw', 'decrypt_raw'
    'encrypt_pkcs1', 'decrypt_pkcs1'
    ]

def create_key_from_primes(primes, e):
    n = phi = 1
    for p in primes:
        n *= p
        phi *= (p-1)
    while True:
        d = nt.mult_inverse(e, phi)
        if d != 0:
            break
        e += 2
    return (n, e, d)

def random_prime(bits):
    n = random.getrandbits(bits) | 1
    while not nt.is_probably_prime(n):
        n += 2
    return n

def create_key_bits(bits, r_count=2, e=0x1001):
    primes = [random_prime(bits) for r in range(r_count)]
    return create_key_from_primes(primes, e)



def encrypt_raw(key, m):
    return nt.powmod(m, key[1], key[0])

def encrypt_pkcs1(key, m):
    k = key[0].bit_length()-1
    data_bits = k - 11*8
    padding_offset = data_bits + 1*8
    cmd_offset = data_bits + 9*8

    raw_m =  (2 << cmd_offset) | (random.getrandbits(8*8) << padding_offset) | m
    return nt.powmod(raw_m, key[1], key[0])



def decrypt_raw(key, c):
    return nt.powmod(c, key[2], key[0])

def decrypt_pkcs1(key, c):
    raw_m = nt.powmod(c, key[2], key[0])

    k = key[0].bit_length()-1
    data_bits = k - 11*8
    padding_offset = data_bits + 1*8
    cmd_offset = data_bits + 9*8

    cmd = raw_m >> cmd_offset
    if cmd != 2:
        return 0
    data = raw_m & ((1 << data_bits) - 1)
    return data


if __name__ == '__main__':
    key = create_key_bits(100)

    print("RAW")
    for m in range(2, 10):
        c = encrypt_raw(key, m)
        m2 = decrypt_raw(key, c)
        print("%d -> %d"%(m, m2))

    print("PKCS1")
    for m in range(2, 10):
        c = encrypt_pkcs1(key, m)
        m2 = decrypt_pkcs1(key, c)
        print("%d -> %d"%(m, m2))

