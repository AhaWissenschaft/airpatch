import re
import sys


def main():
    text = sys.stdin.read()
    words = re.findall(r"[A-Za-z0-9']+", text)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    print("paragraphs", len(paragraphs))
    print("sentences", len(sentences))
    print("words", len(words))
    print("longest", max(words, key=len) if words else "-")


if __name__ == "__main__":
    main()
