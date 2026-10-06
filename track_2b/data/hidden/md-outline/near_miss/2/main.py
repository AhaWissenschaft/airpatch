import re
import sys

HEADING = re.compile(r"(#{1,6}) (.*)")
CLOSING = re.compile(r" #+$")


def slugify(text):
    out = []
    for ch in text.lower():
        if ch == " ":
            out.append("-")
        elif ch == "-" or "a" <= ch <= "z" or "0" <= ch <= "9":
            out.append(ch)
    return "".join(out)


def main():
    counters = [0] * 6
    used = set()
    in_code = False
    for raw in sys.stdin:
        line = raw.rstrip("\n")
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEADING.fullmatch(line)
        if not m:
            continue
        level = len(m.group(1))
        text = m.group(2).strip()
        text = text.rstrip("#").rstrip()
        counters[level - 1] += 1
        for i in range(level, 6):
            counters[i] = 0
        number = ".".join(str(c) for c in counters[:level])
        base = slugify(text)
        slug, n = base, 0
        while slug in used:
            n += 1
            slug = f"{base}-{n}"
        used.add(slug)
        print("  " * (level - 1) + f"{number} {text} (#{slug})")


if __name__ == "__main__":
    main()
