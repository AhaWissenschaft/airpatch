Each line of standard input asks for one conversion and holds three parts
separated by whitespace: `number from to`. Convert `number`, written in base
`from`, to base `to` and print the result on its own line. Empty or blank
lines produce no output.

- Digit values 0 to 35 are written `0`-`9` and then `A`-`Z`. Letters in the
  input may be upper or lower case; letters in the output are upper case.
- A valid number is an optional `-` followed by one or more digits, each
  smaller than the base `from`. Leading zeros are allowed in the input.
  Nothing else is accepted: no `+` sign, no underscores, no prefixes such as
  `0x`, no other characters.
- The output has no leading zeros. Zero (also written `-0` or `000`) is
  printed as `0`; a negative value starts with `-`.
- Bases are written with decimal digits only (no sign) and must be between
  2 and 36.
- Numbers can have up to 100 digits; the conversion is exact.

Print `ERROR` instead if the line does not have exactly three parts, a base
is invalid or out of range, or the number is not valid in base `from`.
