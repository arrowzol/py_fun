#!/usr/bin/python3

import expr
import fraction

expr.addBinaryOp("//", 2, lambda a,b: fraction.Fraction(int(a),int(b)))

vs = {}
while True:
    e = input("expr: ")
    if not e:
        break
    if e == 'vars':
        view = list(vs.items())
        view.sort()
        print('\n'.join(('%s = %s'%(k,repr(v)) for k,v in view)))
    elif e == 'clear':
        vs = {}
    else:
        try:
            e = expr.Expr(e)
            print(repr(e.expr_tree))
            print(repr(e.eval(vs)))
        except expr.ParseException as e:
            print(e)

