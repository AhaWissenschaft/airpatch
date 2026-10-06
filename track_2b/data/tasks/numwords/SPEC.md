Each line of standard input holds one integer `n` with `|n| < 10^15`: an
optional `-` followed by digits (leading zeros are allowed). Leading and
trailing whitespace is ignored; empty or blank lines produce no output.

Print `n` in English words, in lower case, with words separated by single
spaces:

- `0` (also when written `-0` or `000`) is `zero`. A negative number starts
  with the word `minus`: `-15` is `minus fifteen`.
- 1 to 19 are `one`, `two`, ..., `ten`, `eleven`, `twelve`, `thirteen`,
  `fourteen`, ..., `nineteen`. The tens are `twenty`, `thirty`, `forty`,
  `fifty`, `sixty`, `seventy`, `eighty`, `ninety`.
- 21 to 99, when not a multiple of ten, join the two words with a hyphen:
  `forty-two`, `ninety-nine`.
- Hundreds: `one hundred`, `three hundred seven`, `nine hundred ninety-nine`
  (no "and").
- Larger numbers are split into groups of three digits from the right. Each
  non-zero group is written as above, followed by its scale word `thousand`,
  `million`, `billion` or `trillion` (no scale word for the last group), from
  the largest group down. Groups that are zero are left out entirely:
  `1000005` is `one million five` and `2000000` is `two million`.
