Swiss franc amounts are paid in multiples of 5 Rappen (0.05 CHF). Round
every amount to the nearest multiple of 0.05.

Each line of standard input holds one amount: an optional sign (`+` or `-`),
one or more digits, and optionally a decimal point followed by one or more
digits. Leading and trailing whitespace is ignored. Amounts can be long (up
to 30 digits before and 10 digits after the decimal point). Lines that are
empty or contain only whitespace are skipped and produce no output.

For every amount print one line with the rounded amount:

- Rounding is exact (no floating-point error).
- An amount exactly halfway between two multiples of 0.05 is rounded away
  from zero: `0.025` becomes `0.05` and `-1.125` becomes `-1.15`.
- The result is printed with exactly two digits after the decimal point, at
  least one digit before it, and no plus sign: `7` becomes `7.00`.
- A negative result keeps its minus sign, but a result of zero is printed as
  `0.00`, never `-0.00`.
