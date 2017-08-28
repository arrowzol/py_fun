import numtheory as nt


class Fraction(object):
    def __init__(self, n, d=None):
        if d is None:
            n_type = type(n)
            if n_type is int:
                self.__n = n
                self.__d = 1
            elif n_type is str:
                try:
                    nn = n.split("/")
                    if len(nn) == 1:
                        self.__n = int(n)
                        self.__d = 1
                    elif len(nn) == 2:
                        self.__set(int(nn[0]), int(nn[1]))
                    else:
                        raise ValueError()
                except Exception:
                    raise ValueError()
            elif n_type is Fraction:
                self.__n = n.__n
                self.__d = n.__d
            else:
                raise TypeError("Can't construct fraction from non-int")
            return
        if type(n) is not int or type(d) is not int:
            raise TypeError("Can't construct fraction from non-int")
        self.__set(n, d)

    def __set(self, n, d):
        if d == 0:
            raise ZeroDivisionError()
        if n == 0:
            n = 0
            d = 1
        else:
            if d < 0:
                n = -n
                d = -d
            gcd = nt.gcd(n, d)
            n = n // gcd
            d = d // gcd
        self.__n = n
        self.__d = d

    def __bool__(self):
        return bool(self.__n)

    def __add__(self, other):
        ot = type(other)
        if ot is Fraction:
            return Fraction((self.__n * other.__d) + (self.__d * other.__n), self.__d * other.__d)
        elif ot is int:
            return Fraction(self.__n + other * self.__d, self.__d)
        elif ot is float:
            return float(self.__n) / self.__d + other
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    # def __iadd__(self, other):
    #     ot = type(other)
    #     if ot is frac:
    #         x = repr(self) + " += " + repr(other) + " --> "
    #         self.__set((self.__n * other.__d) + (self.__d * other.__n), self.__d * other.__d)
    #         print (x + repr(self))
    #         return self
    #     elif ot is int:
    #         x = repr(self) + " += " + repr(other) + " --> "
    #         self.__n += other*self.__d
    #         print (x + repr(self))
    #         return self
    #     elif ot is float:
    #         return float(self.__n) / self.__d + other
    #     else:
    #         return NotImplemented

    def __sub__(self, other):
        ot = type(other)
        if ot is Fraction:
            return Fraction((self.__n * other.__d) - (self.__d * other.__n), self.__d * other.__d)
        elif ot is int:
            return Fraction(self.__n - other * self.__d, self.__d)
        elif ot is float:
            return float(self.__n) / self.__d - other
        else:
            return NotImplemented

    def __rsub__(self, other):
        ot = type(other)
        if ot is int:
            return Fraction(other * self.__d - self.__n, self.__d)
        elif ot is float:
            return other - float(self.__n) / self.__d
        else:
            return NotImplemented

    # def __isub__(self, other):
    #     ot = type(other)
    #     if ot is frac:
    #         self.__n = (self.__n * other.__d) - (self.__d * other.__n)
    #         self.__d *= other.__d
    #         self.__post()
    #         return self
    #     elif ot is int:
    #         self.__n -= other*self.__d
    #         return self
    #     elif ot is float:
    #         return float(self.__n) / self.__d - other
    #     else:
    #         return NotImplemented
    #
    def __mul__(self, other):
        ot = type(other)
        if ot is Fraction:
            return Fraction(self.__n * other.__n, self.__d * other.__d)
        elif ot is int:
            return Fraction(self.__n * other, self.__d)
        elif ot is float:
            return other * self.__n / self.__d
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    # def __imul__(self, other):
    #     ot = type(other)
    #     if ot is frac:
    #         self.__n *= other.__n
    #         self.__d *= other.__d
    #         self.__post()
    #         return self
    #     elif ot is int:
    #         self.__n *= other
    #         self.__post()
    #         return self
    #     elif ot is float:
    #         return other * self.__n / self.__d
    #     else:
    #         return NotImplemented
    #
    def __truediv__(self, other):
        ot = type(other)
        if ot is Fraction:
            return Fraction(self.__n * other.__d, self.__d * other.__n)
        elif ot is int:
            return Fraction(self.__n, self.__d * other)
        elif ot is float:
            return float(self.__n) / self.__d / other
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        ot = type(other)
        if ot is int:
            return Fraction(self.__d * other, self.__n)
        elif ot is float:
            return other * float(self.__d) / self.__n
        else:
            return NotImplemented

    # def __itruediv__(self, other):
    #     ot = type(other)
    #     if ot is frac:
    #         self.__n *= other.__d
    #         self.__d *= other.__n
    #         self.__post()
    #         return self
    #     elif ot is int:
    #         self.__d *= other
    #         self.__post()
    #         return self
    #     elif ot is float:
    #         return float(self.__n) / self.__d / other
    #     else:
    #         return NotImplemented
    #
    def __str__(self):
        if self.__d == 1:
            return str(self.__n)
        return str(self.__n) + "/" + str(self.__d)

    def __repr__(self):
        return "Fraction(\"" + str(self) + "\")"

if __name__ == "__main__":
    # run tests
    f = Fraction("1/2")
    f += 1
    print(f)
