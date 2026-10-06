import sys


def main():
    text = sys.stdin.read()
    config, _, queries = text.partition("===\n")
    data = {}
    section = ""
    for line in config.splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("["):
            section = line[1:-1]
            continue
        key, value = line.split("=", 1)
        data.setdefault(section, {})[key.strip()] = value.strip()
    for query in queries.splitlines():
        if not query.strip():
            continue
        section, key = query.strip().split(".")
        print(data.get(section, {}).get(key, "NOT FOUND"))


if __name__ == "__main__":
    main()
