Compute the totals of an invoice. Empty lines and lines whose first
non-space character is `#` are ignored; every other line of standard input
is an invoice line:

`<description>;<quantity>;<unit price>;<VAT rate>`

- Spaces around the fields are ignored. The description never contains `;`.
- `<quantity>` is a positive decimal number with at most 3 digits after the
  point. `<unit price>` is a decimal number with at most 2 digits after the
  point; it is negative for credits. `<VAT rate>` is a percentage with at
  most one digit after the point, such as `19`, `7`, `2.6` or `0`. `8` and
  `8.0` are the same rate.

Rounding: every rounding below goes to the stated step, with halves rounded
away from zero (0.125 becomes 0.13, -0.125 becomes -0.13). Use exact decimal
arithmetic, not binary floating point.

1. Line amount = quantity x unit price, rounded to 0.01.
2. For every distinct VAT rate, its net amount is the sum of its line
   amounts, and its VAT is net amount x rate / 100, rounded to 0.01. VAT is
   computed once per rate on the net amount, not per line.
3. The total is the sum of all net amounts and all VAT amounts.
4. The amount payable is the total rounded to 0.05.

Output: one line per VAT rate that occurs, sorted by rate numerically
(smallest first):

`<rate>% net <net amount> vat <VAT>`

with the rate written with exactly one digit after the point (`7.0%`,
`19.0%`, `2.6%`). Then the lines `total <total>` and `payable <payable>`.
All amounts are printed with exactly two digits after the point and a
leading `-` when negative; zero is always printed as `0.00`, never as
`-0.00`. An invoice without lines prints only `total 0.00` and
`payable 0.00`.
