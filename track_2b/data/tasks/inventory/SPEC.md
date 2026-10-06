Each non-empty line of standard input is one command:

- `add <item> <n>`: add `n` units (n is a positive integer).
- `remove <item> <n>`: remove `n` units. If fewer than `n` units are in
  stock, print `ERROR not enough <item>` and change nothing.
- `count <item>`: print `<item> <units>` (0 for an item never added).
- `report`: print every item that has at least one unit as `<item> <units>`,
  sorted by item name, then a final line `total <sum of all units>`.

Any other line (unknown command or wrong number of arguments) prints
`ERROR unknown command`.
