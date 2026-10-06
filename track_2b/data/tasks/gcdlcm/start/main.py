import sys


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def main():
    for line in sys.stdin:
        nums = [int(x) for x in line.split(" ")]
        g = nums[0]
        l = nums[0]
        for n in nums[1:]:
            g = gcd(g, n)
            l = l * n // gcd(l, n)
        print(g, l)


if __name__ == "__main__":
    main()
