Standard input contains lines of the form `name,amount`.

- `amount` is a decimal number with at most two digits after the decimal
  point; it may be negative.
- Spaces around the name and around the amount are ignored.
- Empty lines and lines starting with `#` are ignored.

Print one line per name, `name total`, sorted by name (plain character order,
so upper-case letters come before lower-case letters). The total must be
exact and printed with exactly two digits after the decimal point.
