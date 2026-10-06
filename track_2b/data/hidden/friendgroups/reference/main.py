import sys


def find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def main():
    parent = {}
    for line in sys.stdin:
        names = line.split()
        if not names:
            continue
        for name in names:
            parent.setdefault(name, name)
        if len(names) == 2:
            ra, rb = find(parent, names[0]), find(parent, names[1])
            if ra != rb:
                parent[ra] = rb
    groups = {}
    for name in parent:
        groups.setdefault(find(parent, name), []).append(name)
    members = [sorted(g) for g in groups.values()]
    members.sort(key=lambda g: (-len(g), g[0]))
    for g in members:
        print(" ".join(g))


if __name__ == "__main__":
    main()
