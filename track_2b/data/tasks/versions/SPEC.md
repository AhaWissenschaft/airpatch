Each non-empty line of standard input is a version made of non-negative
integers separated by dots, such as `1.10.2`.

Print the versions sorted in ascending order, comparing them number by
number from the left (so `1.9` comes before `1.10`). Missing numbers count
as 0, so `1.2` and `1.2.0` are equal; leading zeros do not matter (`1.01`
equals `1.1`). Versions that are equal keep their input order.
