Each line of standard input holds zero or more integers separated by
spaces or tabs. Integers may be negative and can have up to 40 digits.

For every line with at least one integer print one line `G L`, where

- `G` is the greatest common divisor of all integers on the line, and
- `L` is their least common multiple.

Both values are never negative; signs do not matter, so `-4 6` gives `2 12`.
The greatest common divisor of integers that are all 0 is 0. If any integer
on the line is 0, the least common multiple is 0. For a single integer `n`
both values are `|n|`. Results must be exact.

Lines without integers (empty or blank lines) produce no output.
