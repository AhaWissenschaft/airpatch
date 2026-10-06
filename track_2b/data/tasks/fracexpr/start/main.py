import sys


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
        left = self.term()
        if self.peek() in ("+", "-"):
            op = self.take()
            right = self.expr()
            return left + right if op == "+" else left - right
        return left

    def term(self):
        left = self.factor()
        if self.peek() in ("*", "/"):
            op = self.take()
            right = self.term()
            return left * right if op == "*" else left / right
        return left

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
            value = Parser(tokenize(line)).expr()
        except ZeroDivisionError:
            print("ERROR")
            continue
        print(value)


if __name__ == "__main__":
    main()
