Simulate a tiny text editor. The document starts empty. Each line of
standard input is one command; the line break at the end of a line is not part
of the command. Empty lines are ignored.

- `type <text>`: append `<text>` to the end of the document. `<text>` is
  everything after the first space of the line (at least one character); it
  may contain spaces, also at its start and at its end.
- `delete <n>`: remove the last `n` characters of the document (`n` is an
  integer, 0 or more). If the document is shorter than `n`, it becomes empty.
- `undo`: revert the most recent change that has not been undone yet. Does
  nothing if there is none.
- `redo`: re-apply the most recently undone change. Does nothing if nothing is
  left to redo.
- `print`: print the document between square brackets, for example
  `[hello world]`.

A *change* is a `type`, or a `delete` that really removes at least one
character. Making a new change discards everything that could still be
redone. A `delete` that removes nothing (because `n` is 0 or the document is
empty) is not a change: it cannot be undone and it does not discard anything
that could be redone. Several undos in a row step back through the changes,
and several redos in a row step forward again.
