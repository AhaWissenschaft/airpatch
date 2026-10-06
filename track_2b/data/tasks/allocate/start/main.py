import sys


def main():
    lines = [line.split() for line in sys.stdin if line.strip()]
    amount = float(lines[0][0])
    people = [(name, int(weight)) for name, weight in lines[1:]]
    total_weight = sum(w for _, w in people)
    for name, w in people:
        share = round(amount * w / total_weight, 2)
        print(name, f"{share:.2f}")


if __name__ == "__main__":
    main()
