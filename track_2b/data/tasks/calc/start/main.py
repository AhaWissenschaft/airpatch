import sys

PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}


def tokenize(text):
    tokens = []
    number = ""
    for ch in text:
        if ch.isdigit():
            number += ch
            continue
        if number:
            tokens.append(int(number))
            number = ""
        if ch in PREC or ch in "()":
            tokens.append(ch)
    if number:
        tokens.append(int(number))
    return tokens


def apply(op, b, a):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a // b
    return a ** b


def evaluate(tokens):
    values, ops = [], []

    def reduce():
        values.append(apply(ops.pop(), values.pop(), values.pop()))

    for tok in tokens:
        if isinstance(tok, int):
            values.append(tok)
        elif tok == "(":
            ops.append(tok)
        elif tok == ")":
            while ops[-1] != "(":
                reduce()
            ops.pop()
        else:
            while ops and ops[-1] != "(" and PREC[ops[-1]] >= PREC[tok]:
                reduce()
            ops.append(tok)
    while ops:
        reduce()
    return values[0]


def main():
    for line in sys.stdin:
        if line.strip():
            try:
                print(evaluate(tokenize(line)))
            except ZeroDivisionError:
                print("error")


if __name__ == "__main__":
    main()
