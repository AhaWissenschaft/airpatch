import sys
from datetime import date

GROUPS = (("child", 0), ("teen", 13), ("adult", 18), ("senior", 65))


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def age_at(born, ref):
    age = ref.year - born.year
    if (ref.month, ref.day) < (born.month, born.day):
        age -= 1
    return age


def group_of(age):
    name = GROUPS[0][0]
    for group, lower in GROUPS:
        if age >= lower:
            name = group
    return name


def main():
    lines = [line.split() for line in sys.stdin if line.strip()]
    ref = parse(lines[0][0])
    counts = {group: 0 for group, _ in GROUPS}
    for name, born in lines[1:]:
        age = int((ref - parse(born)).days / 365.25)
        group = group_of(age)
        counts[group] += 1
        print(name, age, group)
    for group, _ in GROUPS:
        print(group, counts[group])


if __name__ == "__main__":
    main()
