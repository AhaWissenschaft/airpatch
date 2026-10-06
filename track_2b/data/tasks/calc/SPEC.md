Each non-empty line of standard input is an arithmetic expression; print
its value on a line of its own.

Expressions consist of non-negative integer literals (decimal digits), the
binary operators `+`, `-`, `*`, `/` and `^`, unary minus, parentheses and any
number of spaces. All expressions are well-formed and every intermediate value
has at most 30 digits.

Precedence, from tightest to loosest:

1. `^` (power), right-associative: `2^3^2` is `2^(3^2)` = 512. The exponent may
   carry unary minus signs: `2^-1` means `2^(-1)`.
2. Unary minus, which may be repeated: `-2^2` is `-(2^2)` = -4, `--3` is 3.
3. `*` and `/`, left-associative.
4. `+` and `-`, left-associative: `8-3-2` is 3.

`/` is integer division rounding toward zero: `7/2` is 3, `-7/2` is -3,
`7/-2` is -3. `0^0` is 1.

If evaluating the expression divides by zero or raises a number to a negative
power anywhere, print `error` for that line instead of a value.
