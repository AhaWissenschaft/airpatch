import sys


def to_cents(text):
    negative = text.startswith("-")
    if negative:
        text = text[1:]
    whole, _, frac = text.partition(".")
    cents = int(whole) * 100 + int((frac + "00")[:2])
    return -cents if negative else cents


def fmt(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def main():
    lines = [line.split() for line in sys.stdin if line.strip()]
    amount = to_cents(lines[0][0])
    people = [(name, int(weight)) for name, weight in lines[1:]]
    total_weight = sum(w for _, w in people)
    if not people or total_weight == 0:
        print("ERROR")
        return
    a = abs(amount)
    shares = [amount * w // total_weight for _, w in people]
    rests = [amount * w % total_weight for _, w in people]
    missing = amount - sum(shares)
    order = sorted(range(len(people)), key=lambda i: -rests[i])
    for i in order[:missing]:
        shares[i] += 1
    for (name, _), share in zip(people, shares):
        print(name, fmt(share))


if __name__ == "__main__":
    main()
