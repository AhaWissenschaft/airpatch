import sys

MINOR = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "the", "to"}


def headline(line):
    out = []
    for word in line.split():
        if word.lower() in MINOR:
            out.append(word.lower())
        else:
            out.append(word.title())
    return " ".join(out)


def main():
    for line in sys.stdin:
        print(headline(line))


if __name__ == "__main__":
    main()
