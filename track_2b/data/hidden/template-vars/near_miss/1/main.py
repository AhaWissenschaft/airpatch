import re
import sys

PLACEHOLDER = re.compile(r"\{([A-Za-z0-9_]+)\}")


def render(text, variables):
    text = PLACEHOLDER.sub(lambda m: variables.get(m.group(1), m.group(0)), text)
    return text.replace("{{", "{").replace("}}", "}")


def unused(text, variables):
    out = []
    i = 0
    while i < len(text):
        pair = text[i:i + 2]
        if pair == "{{":
            out.append("{")
            i += 2
            continue
        if pair == "}}":
            out.append("}")
            i += 2
            continue
        m = PLACEHOLDER.match(text, i)
        if m:
            out.append(variables.get(m.group(1), m.group(0)))
            i = m.end()
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def main():
    lines = sys.stdin.read().split("\n")
    variables = {}
    if "---" in lines:
        cut = lines.index("---")
        for line in lines[:cut]:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            name, value = line.split("=", 1)
            variables[name.strip()] = value.strip()
        lines = lines[cut + 1:]
    sys.stdout.write(render("\n".join(lines), variables))


if __name__ == "__main__":
    main()
