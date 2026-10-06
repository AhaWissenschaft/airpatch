Standard input holds a table, one row per line, with cells separated by
the character `|`. Print the table with aligned columns.

Reading the table:

- Lines that are empty or contain only spaces and tabs are ignored.
- Spaces and tabs at both ends of every cell are removed.
- The table has as many columns as its longest row; shorter rows are filled
  up with empty cells at the end.
- The first row is the header; all other rows are data rows.

Printing:

- The width of a column is the length of its longest cell (header
  included), but at least 1.
- A column is numeric if it has at least one non-empty data cell and every
  non-empty data cell is a number. A number is an optional `-`, one or more
  digits, and optionally a `.` followed by one or more digits: `7`, `-3`,
  `0.25` and `007` are numbers; `.5`, `1.`, `+5`, `1e3` and `1,000` are
  not.
- Every cell of a numeric column, its header included, is padded with
  spaces on the left up to the column width; cells of all other columns are
  padded on the right.
- Every row is printed as its padded cells joined by ` | `. Directly after
  the header row print a separator line: for every column as many `-` as
  its width, joined by `-+-`.
- Trailing spaces at the end of an output line are not significant.
- Input without rows prints nothing.
