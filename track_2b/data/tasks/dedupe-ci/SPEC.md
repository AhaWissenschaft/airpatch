Read lines from standard input and print them with duplicates removed.

- Two lines are duplicates if they are equal after removing the spaces and
  tabs at both ends and ignoring the case of the letters: `Apple`,
  `  APPLE` and `apple` followed by a tab are all duplicates of each other.
- Spaces and tabs inside a line are significant: `a b`, `a  b` (two spaces)
  and `a`, tab, `b` are three different lines.
- Print only the first occurrence of every line, in input order. Print it
  with the spaces and tabs at both ends removed, but otherwise unchanged
  (it keeps its letter case).
- Lines that are empty after removing spaces and tabs are never printed.
