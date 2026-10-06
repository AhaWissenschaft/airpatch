Swiss social security numbers (AHV numbers) have 13 digits and start with
`756`. They are usually written in groups, as in `756.1234.5678.97`. The last
digit is a check digit computed from the first 12 digits as for EAN-13
barcodes. (All numbers used in this task are fictitious.)

1. Multiply the 1st, 3rd, 5th, ..., 11th digit (counting from the left) by 1
   and the 2nd, 4th, ..., 12th digit by 3.
2. Add up the twelve products. The check digit is the number that must be
   added to this sum to reach the next multiple of 10 (0 if the sum already
   is a multiple of 10).

Each line of standard input holds one number. Leading and trailing
whitespace is ignored, and lines that are empty or contain only whitespace
are skipped (no output). Inside the number, dots and spaces are ignored.
Print one line per number:

- `VALID 756.xxxx.xxxx.xx` if, after removing dots and spaces, there are 13
  digits starting with `756` and the last digit is the correct check digit.
  The number is printed in the standard grouping shown (3, 4, 4 and 2
  digits, separated by dots).
- `INVALID d` if there are 13 digits starting with `756` but the check digit
  is wrong; `d` is the correct check digit.
- `COMPLETE 756.xxxx.xxxx.xx` if there are 12 digits starting with `756`:
  the full number with its check digit appended, in the standard grouping.
- `ERROR` in every other case: a character other than a digit, dot or space,
  a different number of digits (including none), or digits that do not start
  with `756`.
