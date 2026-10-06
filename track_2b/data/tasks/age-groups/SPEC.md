The first line of standard input is the reference date `YYYY-MM-DD`.
Every following non-empty line is `<name> <birth date>` with the birth date
as `YYYY-MM-DD`. No birth date is after the reference date.

A person's age is the number of completed years at the reference date: it
goes up by one on each birthday, and on the birthday itself the new age
already applies. Somebody born on 29 February has their birthday on
1 March in years that are not leap years (so on 28 February of such a year
they still have the old age).

Age groups: `child` 0 to 12, `teen` 13 to 17, `adult` 18 to 64, `senior` 65
and older.

Output: first one line per person in input order, `<name> <age> <group>`.
Then four summary lines, always all four and always in the order `child`,
`teen`, `adult`, `senior`, each as `<group> <number of people in it>` (also
when the number is 0).
