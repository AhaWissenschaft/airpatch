Standard input is a CSV document. Parse every non-empty line as one
record and print its fields, each wrapped in angle brackets, with nothing
between them: the line `a,b` prints `<a><b>`.

- Fields are separated by commas. A line with `n` separating commas has
  `n + 1` fields, so `a,,b,` has four fields and prints `<a><><b><>`.
- A field whose first character is a double quote `"` is quoted. Inside it,
  two double quotes in a row (`""`) stand for one `"` character, commas are
  ordinary characters, and a single `"` ends the field. The surrounding
  quotes are not part of the value. A closing quote is always followed by a
  comma or by the end of the line, and quoted fields never contain line
  breaks.
- A field that does not start with `"` is unquoted and is taken literally,
  including any spaces and any `"` characters in it: `5" pipe` is the value
  `5" pipe`, and ` "x"` (with a leading space) is the value ` "x"`.
- Spaces are never removed from a value.
- Completely empty lines are ignored. A line that contains only spaces is a
  record with one field.
