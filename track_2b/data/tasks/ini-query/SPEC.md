The input is a configuration file in INI format, then a line that is
exactly `===`, then queries. Print the answer to every query.

Reading the configuration (every line first has the spaces and tabs at both
ends removed):

- Empty lines are ignored. Lines starting with `;` or `#` are comments and
  are ignored.
- A line starting with `[` is a section header. The section name is the
  text between the `[` and the first `]`, with spaces removed at both ends;
  anything after the `]` is ignored. Every header line contains a `]`.
- Any other line that contains `=` is a key/value line, split at the first
  `=`. The key is the text before it with spaces removed at both ends.
  Lines without `=` are ignored.
- Keys before the first section header belong to the global section, whose
  name is empty; the header `[]` refers to it as well.
- Section names and keys are case-insensitive. A section may appear several
  times; its keys are merged. If a key appears more than once in a section,
  the last value counts.

The value is the text after the `=` with spaces and tabs removed at both
ends, and then:

- If it starts with `"`, it is quoted: the value is the text between this
  quote and the next `"`, kept exactly (spaces, `;` and `#` included).
  Anything after the closing quote is ignored. Quoted values always have a
  closing quote.
- Otherwise, a `;` or `#` that directly follows a space or tab starts a
  comment: it and everything after it are removed, and then the spaces and
  tabs at the end. A `;` or `#` that does not follow a space or tab (as in
  `a;b`, or at the very start of the value) is part of the value.

Queries: every non-empty line after the `===` line, with spaces at both ends
removed, is a query `section.key`. The key is the text after the last `.`,
the section is the text before it (it may contain dots itself, and it is
empty for a query like `.key`). Names are compared case-insensitively. Print

- the value of the key in that section, if the section has that key;
- otherwise the value of the key in the global section, if it has the key;
- otherwise `NOT FOUND`.

An empty value prints an empty line. Without a `===` line there are no
queries and nothing is printed.
