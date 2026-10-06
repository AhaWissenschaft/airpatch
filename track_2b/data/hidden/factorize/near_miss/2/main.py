import sys


def factorise(n):
    factors = []
    m = abs(n)
    d = 2
    while d * d < m:
        count = 0
        while m % d == 0:
            m //= d
            count += 1
        if count == 1:
            factors.append(str(d))
        elif count > 1:
            factors.append(f"{d}^{count}")
        d += 1 if d == 2 else 2
    if m > 1:
        factors.append(str(m))
    return factors


def main():
    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue
        n = int(text)
        if n in (-1, 0, 1):
            print(f"{n} = {n}")
            continue
        factors = factorise(n)
        if n < 0:
            factors.insert(0, "-1")
        print(f"{n} = " + " * ".join(factors))


if __name__ == "__main__":
    main()
