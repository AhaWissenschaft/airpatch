import sys


def main():
    rows = [[cell.strip() for cell in line.split("|")] for line in sys.stdin if line.strip()]
    if not rows:
        return
    widths = [max(len(cell) for cell in column) for column in zip(*rows)]

    def fmt(row):
        cells = []
        for cell, width in zip(row, widths):
            cells.append(cell.rjust(width) if cell.isdigit() else cell.ljust(width))
        return " | ".join(cells)

    print(fmt(rows[0]))
    print("-+-".join("-" * w for w in widths))
    for row in rows[1:]:
        print(fmt(row))


if __name__ == "__main__":
    main()
