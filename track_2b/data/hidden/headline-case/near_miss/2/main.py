import sys

MINOR = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "the", "to"}


def headline(line):
    words = line.split()
    out = []
    for i, word in enumerate(words):
        if word.lower() in MINOR and i > 0:
            out.append(word.lower())
        else:
            out.append(word[:1].upper() + word[1:].lower())
    return " ".join(out)


def main():
    for line in sys.stdin:
        print(headline(line))


if __name__ == "__main__":
    main()
