class Matrix(object):
    def __init__(self, rows):
        self.__rows = rows

    def solve(self):
        for i in range(len(self.__rows)):
            r = self.__rows[i]
            if r[i]:
                for j in range(len(self.__rows)):
                    if i != j:
                        r2 = self.__rows[j]
                        if r2[i]:
                            scale = r2[i] / r[i]
                            for k in range(len(r)):
                                r2[k] -= r[k] * scale
        for i in range(len(self.__rows)):
            r = self.__rows[i]
            if r[i]:
                scale = r[i]
                for k in range(len(r)):
                    r[k] /= scale

    def rows(self):
        return self.__rows

    def __str__(self):
        return "\n".join(["[" + ", ".join([str(item) for item in row]) + "]" for row in self.__rows])

    def __repr__(self):
        return "m[" + "\n".join(["[" + ", ".join([str(item) for item in row]) + "]" for row in self.__rows]) + "]"


import fraction as f

for i in range(2, 21):
    ml = [[f.Fraction(round(pow(x, y))) for y in range(i, 0, -1)] for x in range(1, i + 1)]
    t = 0
    for l in ml:
        t += l[1]
        l.append(t)
    m = Matrix(ml)
    m.solve()
    print(' '.join(["%8s"%str(x[-1]) for x in m.rows()]))