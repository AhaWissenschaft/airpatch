import re
import sys

WORD = r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*"
TOKEN = re.compile(WORD + r"|[.!?]+")
ABBREVIATIONS = {"mr", "mrs", "dr", "st"}


def paragraphs(lines):
    current = []
    for line in lines:
        if line.strip():
            current.append(line)
        elif current:
            yield "\n".join(current)
            current = []
    if current:
        yield "\n".join(current)


def count_sentences(text):
    count = 0
    has_word = False
    last_word, last_end = "", -1
    for m in TOKEN.finditer(text):
        tok = m.group()
        if tok[0] not in ".!?":
            has_word = True
            last_word, last_end = tok, m.end()
            continue
        if m.end() < len(text) and not text[m.end()].isspace():
            continue
        if tok == "." and last_end == m.start() and last_word.lower() in ABBREVIATIONS:
            continue
        if has_word:
            count += 1
            has_word = False
    if has_word:
        count += 1
    return count


def main():
    paras = list(paragraphs(sys.stdin.read().split("\n")))
    sentences = sum(count_sentences(p) for p in paras)
    words = [w for p in paras for w in re.findall(WORD, p)]
    longest = "-"
    for w in words:
        if longest == "-" or len(w) > len(longest):
            longest = w
    print("paragraphs", len(paras))
    print("sentences", sentences)
    print("words", len(words))
    print("longest", longest)


if __name__ == "__main__":
    main()
