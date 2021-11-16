import numtheory as nt
import rsa

def attack_raw_multiply(mult_by):
    print("raw attach, multiply by %d"%mult_by)

    factor = nt.powmod(mult_by, key[1], key[0])

    for m in range(2, 10):
        c = (rsa.encrypt_raw(key, m) * factor) % key[0]
        m2 = rsa.decrypt_raw(key, c)
        print("%d -> %d"%(m, m2))


def attack_raw_divide(div_by):
    print("raw attack, divide by %d"%div_by)

    factor = nt.powmod(nt.mult_inverse(div_by, key[0]), key[1], key[0])

    for m in range(2, 10):
        c = (rsa.encrypt_raw(key, m) * factor) % key[0]
        m2 = rsa.decrypt_raw(key, c)
        print("%d -> %d"%(m, m2))


def attack_pkcs1(key, c):
    """Attack RSA using PKCS1.
        note: all conforming messages have a plain text value (pt) where 2B <= pt < 3B
            conforming messages are being limited with those with CMD set to 0002
            the rsa.decrpyt(...) method will return 0 when attempting to decrypt a non-conforming message

        m = plain text (message), including all the formatting, of a conforming PKCS1 message
        c = cipher text of m = encrpyt(m)
        2B = the inclusive lower bound of a conforming message
            2B is a conforming message with CMD=0002, and payload and padding having all their bits set to 0
        3B = the exclusive upper bound of a conforming message
            3B-1 is a conforming message with CMD=0002, and payload and padding having all their bits set to 1
        (s_i, c_i) = (s_i = search modifier, c_i = encrypt(m*s_i))
            s_i is chosen so that m*s_i is a conforming message
            finding s_i is done by trial-and-error, calling the decrypt method and only checking if there was an error or not
                note that this is like calling a service that uses decrypt, does not share the decrypted value, but returns an error code if an error is encountered
        M_i = a set of inclsive intervals such that m is in one of those intervals

        the math:
            c = encrypt(m)
            c_i = encrypt(m*s_i) and m*s_i is a conforming message
            condition A: from previous iterations, it is known that m is in one of the intervals in M_i
            condition B: it is also known that m*s_i is in the interval define by:
                2B <= (m*s_i) mod n <= 3B - 1
                2B <= m*s_i + r*n <= 3B - 1, for some integer r
                (2B - r*n) / s_i <= m <= (3B - r*n - 1) / s_i
            condition A and B must both be true, allowing M_i to be computed from s_i and M_(i-1)
            every possible m in M_(i-1) is in M_i, but the reverse is not true, making M_i closer to identifying m
    """

    decrypt_count = 0

    # know the target, just for debugging
    m_target = rsa.decrypt_raw(key, c)

    n,e,d = key
    d = 0 # don't keep the secret key

    k = n.bit_length()-1
    data_bits = k - 11*8
    cmd_offset = data_bits + 9*8
    B = 1 << cmd_offset

    i = 1
    ss = [100000]
    M = [(2*B,3*B-1)]

    while True:
        # check exit condition
        if len(M) == 1:
            a,b = M[0]
            if a == b:
                # Step 4
                print("found={0:80x}".format(a))
                print("   m0={0:80x}".format(m_target))
                print("decrypt op count=%d"%decrypt_count)
                break

        # find m0*si which is conforming, and will divide the remaining search space into 23 pieces
        span = M[-1][1] - M[0][0]
        si = 23 * n // span

        # si should always be increasing
        if si <= ss[-1]:
            si = ss[-1]*53//47 + 1

        while True:
            ci = (c*nt.powmod(si, e, n)) % n
            mi = rsa.decrypt_pkcs1(key, ci)
            decrypt_count += 1
            fail = mi == 0
            if not fail:
                break
            si += 1
        ss.append(si)
        print("====== ====== Si = {0}".format(si))

        # find all overlaping places m0 may be
        Mi = []
        for a,b in M:
            print("--- a={0:80x}\n--- b={1:80x}".format(a,b))
            r = ((a*si - 3*B) // n) + 1

            while True:
                m_min = ((2*B + r*n)-1) // si + 1
                if m_min < a:
                    m_min = a

                m_max = (3*B - 1 + r*n) // si
                if m_max > b:
                    m_max = b

                if m_min > b:
                    break

                print(
"""-  r={0:d}, contains m: {1}
  min={2:80x}
  max={3:80x}""".format(r, m_min <= m_target <= m_max, m_min, m_max))
                if m_min <= m_max:
                    Mi.append((m_min, m_max))
                r += 1

        # merge overlapping intervals together
        Mi.sort()
        M = []
        aa = bb = 0
        for a,b in Mi:
            if aa:
                if bb+1 < a:
                    M.append((aa,bb))
                    aa = a
                    bb = b
                else:
                    bb = b
            else:
                aa = a
                bb = b
        M.append((aa,bb))

        i += 1

if __name__ == '__main__':
    import sys

    key_bits = 100
    if len(sys.argv) >= 3:
        key_bits = int(sys.argv[2])
    key = rsa.create_key_bits(key_bits)

    print("n={0:x} e={1:x} d={2:x}".format(key[0], key[1], key[2]))

    cmd = sys.argv[1]
    if cmd == "mul":
        attack_raw_multiply(2)
        attack_raw_multiply(3)
    if cmd == "div":
        attack_raw_divide(2)
        attack_raw_divide(3)
    if cmd == "pkcs1":
        c = rsa.encrypt_pkcs1(key, 0x123456789abcdef)
        attack_pkcs1(key, c)


