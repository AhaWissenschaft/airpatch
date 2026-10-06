import sys

ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
SCALES = ["", " thousand", " million", " billion", " trillion"]


def below_thousand(n):
    words = ""
    if n >= 100:
        words += ONES[n // 100] + " hundred "
        n %= 100
    if n >= 20:
        words += TENS[n // 10] + " "
        n %= 10
    words += ONES[n]
    return words.strip()


def to_words(n):
    if n == 0:
        return "zero"
    words = ""
    scale = 0
    while n > 0:
        words = below_thousand(n % 1000) + SCALES[scale] + " " + words
        n //= 1000
        scale += 1
    return words.strip()


def main():
    for line in sys.stdin:
        if line.strip():
            print(to_words(int(line)))


if __name__ == "__main__":
    main()
