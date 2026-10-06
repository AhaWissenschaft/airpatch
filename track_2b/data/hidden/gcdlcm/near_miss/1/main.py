import sys


def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def main():
    for line in sys.stdin:
        nums = [int(x) for x in line.split()]
        if not nums:
            continue
        g = 0
        l = 1
        for n in nums:
            g = gcd(g, n)
            l = abs(l * n) // gcd(l, n)
        print(g, l)


if __name__ == "__main__":
    main()
