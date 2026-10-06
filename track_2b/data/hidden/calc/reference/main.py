import sys


class CalcError(Exception):
    pass


def tokenize(text):
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            tokens.append(int(text[i:j]))
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
        tok = self.tokens[self.pos]
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
        value = self.unary()
        while self.peek() in ("*", "/"):
            op = self.take()
            right = self.unary()
            if op == "*":
                value *= right
            else:
                if right == 0:
                    raise CalcError()
                q = abs(value) // abs(right)
                value = q if (value >= 0) == (right >= 0) else -q
        return value

    def unary(self):
        if self.peek() == "-":
            self.take()
            return -self.unary()
        return self.power()

    def power(self):
        base = self.atom()
        if self.peek() == "^":
            self.take()
            exponent = self.unary()
            if exponent < 0:
                raise CalcError()
            return base ** exponent
        return base

    def atom(self):
        tok = self.take()
        if tok == "(":
            value = self.expr()
            self.take()
            return value
        return tok


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            print(Parser(tokenize(line)).expr())
        except CalcError:
            print("error")


if __name__ == "__main__":
    main()
