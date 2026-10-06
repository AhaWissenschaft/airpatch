import sys
from collections import Counter


def top_words(text, n=3):
    words = text.lower().split()
    return Counter(words).most_common(n)


def main():
    for word, count in top_words(sys.stdin.read()):
        print(word, count)


if __name__ == "__main__":
    main()
