#!/usr/local/bin/python3

import re
import math

########################################
# Expression Classes
########################################

class Expr(object):
    def __init__(self, expr_text=None, tokens=None):
        if not tokens:
            tokens = lex(expr_text)
        self.orig_tokens = tokens
        self.__unparsed_tokens, self.orig_expr_tree = parse(tokens)
        self.expr_tree = fold_constants(self.orig_expr_tree)
        self.expr_func = tree_to_func(self.expr_tree)
        if expr_text and self.__unparsed_tokens:
            raise Exception("error at " + repr(self.__unparsed_tokens))

        # compute required variables
        self.var_names = set()
        self.assign_names = set()
        get_sets(self.var_names, self.assign_names, self.expr_tree)

    def get_unparsed_tokens(self):
        tokens = self.__unparsed_tokens
        self.__unparsed_tokens = None
        return tokens

    def eval(self, vs):
        return self.expr_func(vs)

    def get_assigned_name(self):
        if self.expr_tree[0] == "assign":
            return self.expr_tree[1]

class ExprSet(object):
    def __init__(self, expr_text=None, file_name=None):
        if file_name:
            tokens = lex_file(file_name)
        else:
            tokens = lex(expr_text)
        self.exprs = []
        self.exprs_by_name = {}
        while tokens:
            new_expr = Expr(tokens=tokens)
            self.exprs.append(new_expr)

            name = new_expr.get_assigned_name()
            if name:
                self.exprs_by_name[name] = new_expr

            tokens = new_expr.get_unparsed_tokens()
            if tokens and tokens[0][0] == "delim":
                tokens = tokens[1:]

    def eval_name(self, name, missing=None):
        if name in self.exprs_by_name:
            vs = {}
            self.exprs_by_name[name].eval(vs)
            return vs[name]
        else:
            return missing

    def eval(self, vs):
        return [expr.eval(vs) for expr in self.exprs]

########################################
# Lexer
########################################

LEX_TOKENS = [
        (r"\d*[.]\d+", "lit_float"),
        (r"\d+", "lit_int"),
        (r"=", "op1"),
        (r"[*/]", "op2"),
        (r"[-+]", "op3"),
        (r"[(]", "open"),
        (r"[)]", "close"),
        (r"[,]", "delim"),
        (r"[A-Za-z_][A-Za-z0-9_]*", "name"),
]

LEX_TOKENS = [(re.compile(r"\s*(" + t1 + ")"), t2) for t1, t2 in LEX_TOKENS]

def lex(expr_text):
    tokens = []
    position = 0
    while expr_text:
        for t1, t2 in LEX_TOKENS:
            m = t1.match(expr_text)
            if m:
                tokens.append((t2, m.group(1)))
                position += m.end()
                expr_text = expr_text[m.end():]
                break
        else:
            raise Exception("can't tokenize at " + expr_text)
    return tokens

def lex_file(file_name):
    with open(file_name) as open_file:
        return [
            token
            for line in open_file
            for token in lex(line.rstrip())]

########################################
# Parser
########################################

FUNC_NAMES = set()
FUNC_NAMES.add("sin")
FUNC_NAMES.add("cos")

def parse(tokens):
    """
    an expr_tree node has the following forms:
        ("assign", name, expr_tree)
        ("var", name)
        ("func", name, expr_tree)
        ("binop", op, expr1_tree, expr2_tree)
        ("lit_int", int)
        ("lit_float", float)

    :return: (remaning tokens, expr_tree)
    """
    if tokens:
        tokens, expr1_tree = parse_leaf(tokens)
        return parse_expr3(tokens, expr1_tree)
    return (None, None)

def parse_expr3(tokens, expr1_tree):
    "Expect binary ops (+, -)"

    tokens, expr1_tree = parse_expr2(tokens, expr1_tree)
    if not tokens:
        return (tokens, expr1_tree)

    top_token = tokens[0]
    tok_type = top_token[0]
    tok_value = top_token[1]

    if tok_type == "op3":
        tokens, expr2_tree = parse_leaf(tokens[1:])
        tokens, expr2_tree = parse_expr2(tokens, expr2_tree)
        return parse_expr3(tokens, ("binop", tok_value, expr1_tree, expr2_tree))
    return (tokens, expr1_tree)

def parse_expr2(tokens, expr1_tree):
    "Expect binary ops (*, /)"

    tokens, expr1_tree = parse_expr1(tokens, expr1_tree)
    if not tokens:
        return (tokens, expr1_tree)

    top_token = tokens[0]
    tok_type = top_token[0]
    tok_value = top_token[1]

    if tok_type == "op2":
        tokens, expr2_tree = parse_leaf(tokens[1:])
        tokens, expr2_tree = parse_expr1(tokens, expr2_tree)
        return parse_expr2(tokens, ("binop", tok_value, expr1_tree, expr2_tree))
    return (tokens, expr1_tree)

def parse_expr1(tokens, expr1_tree):
    "Expect binary ops (=)"

    if not tokens:
        return (tokens, expr1_tree)

    top_token = tokens[0]
    tok_type = top_token[0]

    if tok_type == "op1":
        if expr1_tree[0] != "var":
            raise Exception("LHS must be a variable name " + repr(tokens))
        tokens, expr2_tree = parse(tokens[1:])
        name = expr1_tree[1]
        return parse_expr1(tokens, ["assign", name, expr2_tree])
    return (tokens, expr1_tree)

def parse_leaf(tokens):
    "Expect literals, variables, function calls, and parenthases"
    top_token = tokens[0]
    tok_type = top_token[0]
    tok_value = top_token[1]

    if tok_type == "lit_int":
        return (tokens[1:], top_token)
    elif tok_type == "lit_float":
        return (tokens[1:], top_token)
    elif tok_type == "name":
        return parse_name(tokens[1:], tok_value)
    elif tok_type == "open":
        tokens, expr_tree = parse(tokens[1:])
        if tokens and tokens[0][0] == "close":
            return (tokens[1:], expr_tree)
        else:
            raise Exception("missing closing paren at " + repr(tokens))
    raise Exception("parse error at " + repr(tokens))

def parse_name(tokens, name):
    if tokens:
        tok_type = tokens[0][0]
        if tok_type == "open":
            tokens, expr_tree = parse(tokens[1:])
            if tokens and tokens[0][0] == "close":
                if name not in FUNC_NAMES:
                    raise Excpetion("uknown function " + name)
                return (tokens[1:], ("func", name, expr_tree))
            else:
                raise Exception("missing closing paren at " + repr(tokens))
    if name == "pi":
        return (tokens, ("lit_float", name))
    return (tokens, ("var", name))

########################################
# Parse tree utilities
########################################

def tree_to_func(expr_tree):
    node_type = expr_tree[0]

    if node_type == "assign":
        node_type, name, expr_tree = expr_tree
        expr_func = tree_to_func(expr_tree)
        def expr2_func(vs):
            answer = expr_func(vs)
            vs[name] = answer
            return answer
        return expr2_func
    if node_type == "var":
        return lambda vs: vs[expr_tree[1]]
    if node_type == "func":
        node_type, name, expr_tree = expr_tree
        expr_func = tree_to_func(expr_tree)
        if name == "sin":
            return lambda vs: math.sin(expr_func(vs))
        elif name == "cos":
            return lambda vs: math.cos(expr_func(vs))
    if node_type == "binop":
        node_type, name, expr1_tree, expr2_tree = expr_tree
        expr1_func = tree_to_func(expr1_tree)
        expr2_func = tree_to_func(expr2_tree)
        if name == "+":
            return lambda vs: expr1_func(vs) + expr2_func(vs)
        if name == "-":
            return lambda vs: expr1_func(vs) - expr2_func(vs)
        if name == "*":
            return lambda vs: expr1_func(vs) * expr2_func(vs)
        if name == "/":
            return lambda vs: expr1_func(vs) / expr2_func(vs)
    if node_type == "lit_int":
        int_value = int(expr_tree[1])
        return lambda vs: int_value
    if node_type == "lit_float":
        float_value = expr_tree[1]
        if float_value == "pi":
            float_value = math.pi
        else:
            float_value = float(float_value)
        return lambda vs: float_value
    raise Exception("bad parse tree type: %s"%(node_type))

def is_const_node(expr_tree):
    return expr_tree[0].startswith("lit_")

def fold_constants(expr_tree):
    "Fold constants in the parse tree"
    node_type = expr_tree[0]

    is_const = False
    if node_type in ["assign", "func"]:
        expr1_tree = fold_constants(expr_tree[2])
        expr_tree = (node_type, expr_tree[1], expr1_tree)
        is_const = node_type == "func" and is_const_node(expr1_tree)
    elif node_type == "binop":
        expr1_tree = fold_constants(expr_tree[2])
        expr2_tree = fold_constants(expr_tree[3])
        expr_tree = (node_type, expr_tree[1], expr1_tree, expr2_tree)
        is_const = is_const_node(expr1_tree) and is_const_node(expr2_tree)
    if is_const:
        const_value = tree_to_func(expr_tree)(None)
        if type(const_value) == int:
            return ("lit_int", const_value)
        else:
            return ("lit_float", const_value)
    return expr_tree

def get_sets(var_names, assign_names, expr_tree):
    node_type = expr_tree[0]

    if node_type == "var":
        var_names.add(expr_tree[1])
    elif node_type == "assign":
        assign_names.add(expr_tree[1])
        var_names.add(expr_tree[2])
    elif node_type == "func":
        get_sets(var_names, assign_names, expr_tree[2])
    elif node_type == "binop":
        get_sets(var_names, assign_names, expr_tree[2])
        get_sets(var_names, assign_names, expr_tree[3])

########################################
# Testing
########################################

if __name__ == "__main__":
    vs = {'a': 1, 'b': 2, 'c': 3}
    while True:
        e = input("expr: ")
        if not e:
            break
        e = Expr(e)
        print(repr(e.orig_tokens))
        print(repr(e.orig_expr_tree))
        print(repr(e.expr_tree))
        print(repr(e.eval(vs)))
    while True:
        e = input("expr set: ")
        if not e:
            break
        e = ExprSet(e)
        print(repr(e.eval(vs)))


