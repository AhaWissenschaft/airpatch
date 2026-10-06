import sys


def main():
    group_of = {}
    groups = []
    for line in sys.stdin:
        names = line.split()
        if not names:
            continue
        first, last = names[0], names[-1]
        if first in group_of:
            g = group_of[first]
        elif last in group_of:
            g = group_of[last]
        else:
            g = len(groups)
            groups.append(set())
        for name in names:
            group_of[name] = g
            groups[g].add(name)
    groups.sort(key=lambda s: (-len(s), min(s)))
    for g in groups:
        print(" ".join(sorted(g)))


if __name__ == "__main__":
    main()
