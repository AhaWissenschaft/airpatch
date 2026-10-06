import sys


def spiral(m):
    out = []
    if not m:
        return out
    top, bottom, left, right = 0, len(m) - 1, 0, len(m[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            out.append(m[top][j])
        for i in range(top + 1, bottom + 1):
            out.append(m[i][right])
        if top < bottom:
            for j in range(right - 1, left - 1, -1):
                out.append(m[bottom][j])
        for i in range(bottom - 1, top, -1):
            out.append(m[i][left])
        top, bottom, left, right = top + 1, bottom - 1, left + 1, right - 1
    return out


def main():
    m = [line.split() for line in sys.stdin if line.strip()]
    values = spiral(m)
    if values:
        print(" ".join(values))


if __name__ == "__main__":
    main()
