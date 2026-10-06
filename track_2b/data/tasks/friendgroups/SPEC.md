Each non-empty line of standard input names one or two people, separated
by whitespace:

- `a b` means that `a` and `b` are friends;
- a line with a single name only says that this person exists;
- a line `a a` is the same as a line `a`.

Friendship groups are formed by chains of friendships: if `a` is a friend of
`b` and `b` is a friend of `c`, then `a`, `b` and `c` belong to the same
group, even if `a` and `c` never appear on the same line. Every person named
anywhere in the input belongs to exactly one group. Names are case-sensitive
(`Bob` and `bob` are different people).

Print one line per group: the names of its members sorted in plain character
order (upper-case letters before lower-case letters), separated by single
spaces. Print larger groups first; groups of the same size are ordered by
their first (smallest) name, ascending. Empty input gives no output.
