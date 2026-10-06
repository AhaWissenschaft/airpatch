Each line of standard input holds one date, possibly with spaces or tabs
around it. Convert every date between the Swiss and the ISO format.

- A Swiss date `D.M.YYYY` has a day and a month of one or two digits and a
  year of exactly four digits, separated by dots (`5.3.2024`,
  `05.03.2024`). Print it in ISO format `YYYY-MM-DD` with a two-digit month
  and day (`2024-03-05`).
- An ISO date `YYYY-MM-DD` has exactly four, two and two digits separated
  by hyphens (`2024-03-05`). Print it in Swiss format `DD.MM.YYYY` with a
  two-digit day and month (`05.03.2024`).
- Print `invalid` for a line that matches neither format exactly, and for a
  date that does not exist in the Gregorian calendar: day or month `0`,
  month above `12`, a day beyond the end of the month (`31.04.2024`,
  `29.02.2023`), or the year `0000`. Leap years are the years divisible by
  4, except years divisible by 100 but not by 400.
- Lines that are empty or contain only spaces and tabs print nothing.
