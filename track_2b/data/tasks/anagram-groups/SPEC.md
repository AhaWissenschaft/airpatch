Read a text from standard input and print its groups of anagrams.

- A word is a maximal run of the letters `a`-`z` and `A`-`Z`; every other
  character separates words. Words are compared in lower case, so `Listen`
  and `listen` are the same word.
- Two different words are anagrams if one is a rearrangement of the letters
  of the other, using every letter exactly as often (`stop` and `pots` are
  anagrams, `stop` and `spots` are not).
- A group is a set of at least two different words that are all anagrams of
  each other; each group contains every such word of the text. A word that
  occurs several times counts once.
- Print one group per line: its words in lower case, sorted alphabetically,
  separated by single spaces.
- Order the groups by size, largest first; groups of the same size are
  ordered alphabetically by their first printed word.
- Print nothing if the text has no group.
