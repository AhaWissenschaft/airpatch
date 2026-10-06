Each non-empty line of standard input is a match result
`home away hg-ag`, for example `Lions Tigers 2-1` (the home team scored `hg`
goals, the away team `ag`). Team names contain no spaces; a team never plays
itself. A win gives 3 points, a draw 1 point, a loss 0 points.

Print the league table, one line per team:

`<rank> <team> <played> <won> <drawn> <lost> <goals for>:<goals against> <points>`

Teams are ordered by

1. points, highest first;
2. goal difference (goals for minus goals against), highest first;
3. goals for, highest first;
4. team name in plain character order (upper-case letters before lower-case).

Teams that are equal in points, goal difference and goals for share the same
rank; the following rank skips the shared places (ranks `1 2 2 4`, not
`1 2 2 3`). Empty input gives no output.
