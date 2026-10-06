import sys


def main():
    deps = {}
    for line in sys.stdin:
        if not line.strip():
            continue
        name, _, rest = line.partition(":")
        deps.setdefault(name.strip(), []).extend(rest.split())
    done = set()
    order = []

    def visit(task):
        if task in done:
            return
        done.add(task)
        for d in sorted(deps.get(task, [])):
            visit(d)
        order.append(task)

    for task in sorted(deps):
        visit(task)
    for task in order:
        print(task)


if __name__ == "__main__":
    main()
