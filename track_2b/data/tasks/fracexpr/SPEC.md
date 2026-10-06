Each line of standard input is an arithmetic expression. Evaluate it
exactly, with fractions, and print the result. Empty or blank lines produce
no output.

Expressions are built from:

- non-negative integers written with decimal digits (they can be long),
- the binary operators `+`, `-`, `*` and `/`,
- unary minus: a `-` at the start of the expression, after `(` or after
  another operator negates the number, parenthesised expression or
  unary-minus expression that directly follows it (`-3`, `2 * -3`,
  `-(1 + 2)`, `--4`),
- parentheses.

Spaces may appear between any two tokens or be left out (`10/4-1/4`).

Rules:

- `*` and `/` bind more strongly than `+` and `-`.
- Binary operators of the same strength are applied from left to right:
  `8 - 3 - 2` is `3` and `8 / 4 / 2` is `1`.
- `/` is exact division: `1 / 3` is one third.

Output: a whole result is printed as an integer (`4`, `-7`, `0`); any other
result as a fully reduced fraction `p/q` with `q > 1` and the sign, if any,
in front of `p` (`5/6`, `-1/2`). If a division by zero happens anywhere while
evaluating the expression, print `ERROR` instead.

Every non-blank line is a well-formed expression.
