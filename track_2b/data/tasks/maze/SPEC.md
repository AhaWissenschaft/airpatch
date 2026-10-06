Standard input is a rectangular maze, one row per line; all rows have the
same length. Empty lines are ignored. The characters are:

- `#` a wall,
- `.` a free cell,
- `S` the start (exactly one),
- `E` an exit (there may be any number of exits, also none).

In one step you can move from a cell to the neighbouring cell above, below,
left or right of it, but never into a wall and never outside the maze. `S` and
`E` cells are free cells.

Print the smallest number of steps needed to get from `S` to any exit. If no
exit can be reached, print `NO PATH`.
