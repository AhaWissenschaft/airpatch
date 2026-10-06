For every line of standard input print the line in headline case.

- A word is a maximal run of characters other than spaces and tabs. Print
  the words of a line separated by single spaces; spaces and tabs at the
  start, at the end and between words are not kept. A line without words
  prints an empty line.
- The minor words are `a an and as at but by for in nor of on or the to`.
  A word is minor if it equals one of them when letter case is ignored;
  attached punctuation makes it a different word (`the,` is not minor).
- A minor word is printed entirely in lower case, unless it is the first
  or the last word of its line.
- Every other word, and a minor word that is the first or last word, is
  printed with its first character in upper case and all remaining
  characters in lower case: `o'BRIEN` becomes `O'brien`, `x-ray` becomes
  `X-ray` and `3RD` becomes `3rd`.
