import sys


def parse_value(raw):
    value = raw.strip()
    if value.startswith('"'):
        return value[1:value.index('"', 1)]
    for mark in ";#":
        value = value.split(mark)[0]
    return value.rstrip()


def main():
    lines = sys.stdin.read().split("\n")
    if "===" in lines:
        cut = lines.index("===")
        config, queries = lines[:cut], lines[cut + 1:]
    else:
        config, queries = lines, []
    data = {"": {}}
    section = ""
    for raw in config:
        line = raw.strip()
        if not line or line[0] in ";#":
            continue
        if line.startswith("["):
            section = line[1:line.index("]")].strip().lower()
            data.setdefault(section, {})
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        data.setdefault(section, {})[key.strip().lower()] = parse_value(value)
    for raw in queries:
        query = raw.strip()
        if not query:
            continue
        sec, _, key = query.rpartition(".")
        sec, key = sec.lower(), key.lower()
        if key in data.get(sec, {}):
            print(data[sec][key])
        elif key in data[""]:
            print(data[""][key])
        else:
            print("NOT FOUND")


if __name__ == "__main__":
    main()
