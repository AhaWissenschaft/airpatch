import re
import sys
from collections import Counter


def top_words(text, n=3):
    counts = Counter(re.findall(r"[a-z0-9']+", text.lower()))
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:n]


def main():
    for word, count in top_words(sys.stdin.read()):
        print(word, count)


if __name__ == "__main__":
    main()
