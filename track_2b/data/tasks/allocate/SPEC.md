Split an amount of money between several people in proportion to their
weights, in whole cents, so that the shares add up exactly to the amount.

Input: lines that are empty or contain only whitespace are ignored. The first
remaining line (there always is one) is the amount: an optional `-`, digits,
and optionally a `.` followed by one or two digits (`100`, `12.5`, `-0.10`).
Amounts can be very large. Every further line is `name weight`: a name
without spaces (all names differ) and a weight, a non-negative integer.

Method, with `A` the absolute value of the amount in cents and `W` the sum of
all weights:

1. The exact share of a person with weight `w` is `A * w / W` cents.
2. Everyone first gets their exact share rounded down to whole cents.
3. The cents still missing to reach `A` are given out one each to the people
   whose exact shares had the largest fractional parts (the parts cut off in
   step 2). Among equal fractional parts, the person listed earlier in the
   input comes first. Nobody gets more than one extra cent.
4. If the amount is negative, every share is negated.

Output: one line per person, in input order: `name share`, with the share
printed with exactly two digits after the decimal point (`33.34`, `-0.04`,
`0.00`; never `-0.00`).

If there are no people, or all weights are 0, print only `ERROR`.
