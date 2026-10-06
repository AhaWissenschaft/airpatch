import sys
from fractions import Fraction


def tokenize(text):
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch in "0123456789":
            j = i
            while j < len(text) and text[j] in "0123456789":
                j += 1
            tokens.append(text[i:j])
            i = j
        else:
            tokens.append(ch)
            i += 1
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expr(self):
        value = self.term()
        while self.peek() in ("+", "-"):
            if self.take() == "+":
                value += self.term()
            else:
                value -= self.term()
        return value

    def term(self):
        value = self.factor()
        while self.peek() in ("*", "/"):
            if self.take() == "*":
                value *= self.factor()
            else:
                value /= self.factor()
        return value

    def factor(self):
        tok = self.take()
        if tok == "-":
            return -self.factor()
        if tok == "(":
            value = self.expr()
            self.take()
            return value
        return int(tok)


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            value = Fraction(Parser(tokenize(line)).expr()).limit_denominator()
        except ZeroDivisionError:
            print("ERROR")
            continue
        print(value)


if __name__ == "__main__":
    main()
