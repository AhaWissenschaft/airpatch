import sys


def main():
    text = sys.stdin.read()
    head, _, body = text.partition("---\n")
    variables = {}
    for line in head.splitlines():
        if "=" in line:
            name, value = line.split("=")
            variables[name.strip()] = value.strip()
    for name, value in variables.items():
        body = body.replace("{" + name + "}", value)
    body = body.replace("{{", "{").replace("}}", "}")
    sys.stdout.write(body)


if __name__ == "__main__":
    main()
