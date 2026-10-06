import sys
from datetime import date


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def main():
    lines = [line.split() for line in sys.stdin if line.strip()]
    ref = parse(lines[0][0])
    counts = {}
    for name, born in lines[1:]:
        age = ref.year - parse(born).year
        if age < 13:
            group = "child"
        elif age < 18:
            group = "teen"
        elif age < 65:
            group = "adult"
        else:
            group = "senior"
        counts[group] = counts.get(group, 0) + 1
        print(name, age, group)
    for group in counts:
        print(group, counts[group])


if __name__ == "__main__":
    main()
