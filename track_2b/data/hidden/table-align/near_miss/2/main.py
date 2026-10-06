import re
import sys

NUMBER = re.compile(r"-?[0-9]+(\.[0-9]+)?")


def is_number(text):
    return NUMBER.fullmatch(text) is not None


def main():
    rows = [[cell.strip() for cell in line.split("|")] for line in sys.stdin if line.strip()]
    if not rows:
        return
    ncol = max(len(row) for row in rows)
    for row in rows:
        row.extend([""] * (ncol - len(row)))
    widths = [max(1, max(len(row[c]) for row in rows)) for c in range(ncol)]
    numeric = []
    for c in range(ncol):
        data = [row[c] for row in rows[1:]]
        numeric.append(bool(data) and all(is_number(cell) for cell in data))

    def fmt(row):
        return " | ".join(row[c].rjust(widths[c]) if numeric[c] else row[c].ljust(widths[c])
                          for c in range(ncol))

    print(fmt(rows[0]))
    print("-+-".join("-" * w for w in widths))
    for row in rows[1:]:
        print(fmt(row))


if __name__ == "__main__":
    main()
