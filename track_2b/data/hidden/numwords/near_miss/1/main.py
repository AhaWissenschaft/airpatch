import sys

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
SCALES = ["", "thousand", "million", "billion", "trillion"]


def below_thousand(n):
    words = []
    if n >= 100:
        words.append(ONES[n // 100] + " hundred")
        n %= 100
    if n >= 20:
        words.append(TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else ""))
    elif n > 0:
        words.append(ONES[n])
    return " ".join(words)


def to_words(n):
    if n == 0:
        return "zero"
    groups = []
    scale = 0
    while n:
        n, group = divmod(n, 1000)
        if group:
            groups.append(below_thousand(group) + (" " + SCALES[scale] if scale else ""))
        scale += 1
    return " ".join(reversed(groups))


def main():
    for line in sys.stdin:
        text = line.strip()
        if text.startswith("-"):
            print("minus " + to_words(int(text[1:])))
        elif text:
            print(to_words(int(text)))


if __name__ == "__main__":
    main()
