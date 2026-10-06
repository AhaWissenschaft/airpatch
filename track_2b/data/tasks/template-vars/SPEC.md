The input consists of variable definitions, a line that is exactly `---`,
and a template. Print the template with its placeholders filled in.

Definitions (all lines before the first line that is exactly `---`):

- Lines that are empty or contain only spaces, and lines whose first
  non-space character is `#`, are ignored.
- Every other line has the form `name=value`. The name is the text before
  the first `=`, the value is the text after it; spaces at both ends of the
  name and of the value are removed. The value may contain any characters,
  including `=`, `{` and `}`. Names consist of letters, digits and
  underscores and are case-sensitive. If a name is defined more than once,
  the last definition counts.
- If the input has no `---` line, there are no definitions and the whole
  input is the template.

The template (everything after the first `---` line, including any later
`---` lines) is processed from left to right. At every position the first
matching rule applies:

1. `{{` produces `{`.
2. `}}` produces `}`.
3. `{name}`, where `name` is one or more letters, digits or underscores,
   produces the value of the variable `name`. If `name` is not defined, the
   placeholder is copied unchanged. Processing continues after its `}`.
4. Any other character is copied unchanged.

Values are inserted exactly as defined; braces inside an inserted value are
not processed again. The line structure of the template is kept.
