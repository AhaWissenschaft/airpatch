Standard input holds integers separated by any whitespace (spaces, tabs,
line breaks). They may be negative and can be large. Print a summary of
five lines:

```
count <number of values>
mean <mean>
median <median>
mode <mode>
range <largest value minus smallest value>
```

- `mean` is the exact arithmetic mean, rounded to two digits after the
  decimal point and always printed with exactly two such digits. A mean
  exactly halfway between two candidates is rounded away from zero (`0.125`
  becomes `0.13`, `-0.125` becomes `-0.13`). A mean that rounds to zero is
  printed as `0.00`, never `-0.00`.
- `median` is the middle value of the sorted values; for an even count it is
  the mean of the two middle values. It is printed exactly: as an integer if
  it is a whole number, otherwise with `.5` (`2.5`, `-0.5`).
- `mode` is the value that occurs most often; if several values occur equally
  often, the smallest of them.

If there are no values at all, print only the line `count 0`.
