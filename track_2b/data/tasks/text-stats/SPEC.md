Read a text from standard input and print four lines:

```
paragraphs <number of paragraphs>
sentences <number of sentences>
words <number of words>
longest <longest word>
```

Definitions:

- A blank line is empty or contains only spaces and tabs. A paragraph is a
  maximal group of consecutive non-blank lines.
- A word is a maximal run of letters `a`-`z`, `A`-`Z` and digits `0`-`9`,
  where a single `'` or `-` that has a letter or digit directly on both
  sides also belongs to the word. So `don't`, `x-ray` and `rock'n'roll` are
  single words, `well--known` is the two words `well` and `known`,
  `'quoted'` is the word `quoted`, and `3.14` is the two words `3` and `14`.
- A terminator is a maximal run of the characters `.`, `!` and `?` (such as
  `.`, `?!` or `...`).
- Sentences are counted per paragraph. A terminator ends a sentence if it
  is followed by whitespace (a space, tab or line break inside the
  paragraph) or stands at the end of the paragraph. Exception: a terminator
  that is a single `.` directly after (with nothing in between) one of the
  words `Mr`, `Mrs`, `Dr` or `St`, compared ignoring case, does not end a
  sentence. The end of a paragraph always ends a sentence. A sentence is
  counted only if it contains at least one word.
- `longest` is the longest word, as written in the text; if several words
  share the greatest length, the first of them. Print `-` if the text has
  no words.
