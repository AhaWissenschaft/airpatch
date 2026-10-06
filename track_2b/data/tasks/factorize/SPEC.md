Each line of standard input holds one integer `n` with `|n| <= 10^12`:
an optional `-` followed by digits (leading zeros are allowed). Leading and
trailing whitespace is ignored; empty or blank lines produce no output.

For every integer print one line `n = factorisation`, with `n` printed as a
plain integer (no leading zeros):

- The prime factors of `|n|` are listed in increasing order, separated by
  ` * ` (space, star, space).
- A prime that divides `|n|` exactly `k` times is written `p^k` if `k > 1`
  and just `p` if `k = 1`: `360 = 2^3 * 3^2 * 5`.
- For a negative `n` the list starts with `-1`: `-12 = -1 * 2^2 * 3`.
- A prime is its own factorisation: `13 = 13`.
- Special values: `0 = 0`, `1 = 1` and `-1 = -1`.
