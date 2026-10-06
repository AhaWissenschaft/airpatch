Each line of standard input holds a calculation `a op b`: two decimal
numbers and an operator, separated by whitespace. Empty or blank lines
produce no output.

- A number is an optional `-`, one or more digits, and optionally a `.`
  followed by one or more digits (`12`, `-0.5`, `003.140`). Numbers can have
  up to 60 digits.
- `op` is `+`, `-`, `*` or `/`.

`+`, `-` and `*` give the exact result. `/` gives the quotient rounded to 10
digits after the decimal point; a quotient exactly halfway between two such
values is rounded away from zero. Division by zero prints `ERROR`.

Results are printed in plain decimal notation:

- no exponent notation and no `+` sign;
- no leading zeros, except a single `0` before the decimal point when the
  integer part is zero (`0.25`, `-0.25`);
- no trailing zeros after the decimal point, and no decimal point at all for
  a whole number (`1.50 + 1.50` gives `3`);
- zero is printed as `0`, never `-0`.
