import sys


def spiral(m):
    out = []
    n = len(m)
    for layer in range((n + 1) // 2):
        last = n - 1 - layer
        for j in range(layer, last + 1):
            out.append(m[layer][j])
        for i in range(layer + 1, last + 1):
            out.append(m[i][last])
        for j in range(last - 1, layer - 1, -1):
            out.append(m[last][j])
        for i in range(last - 1, layer, -1):
            out.append(m[i][layer])
    return out


def main():
    m = [line.split() for line in sys.stdin if line.strip()]
    values = spiral(m)
    if values:
        print(" ".join(values))


if __name__ == "__main__":
    main()
