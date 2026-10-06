import sys


def main():
    for line in sys.stdin:
        n = int(line)
        factors = []
        m = n
        d = 2
        while d * d <= m:
            count = 0
            while m % d == 0:
                m //= d
                count += 1
            if count:
                factors.append(f"{d}^{count}")
            d += 1
        print(f"{n} = " + " * ".join(factors))


if __name__ == "__main__":
    main()
