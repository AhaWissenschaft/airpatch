Standard input is a Markdown document. Print a numbered outline of its
headings.

Headings:

- A heading is a line that starts with 1 to 6 `#` characters followed by a
  space; the number of `#` is its level. `#tag`, a line starting with seven
  or more `#`, and a line starting with a space are not headings.
- Lines inside fenced code blocks are never headings. A line that starts
  with three backticks (possibly followed by more text, such as a language
  name) opens a code block, and the next such line closes it; the fence
  lines themselves are not headings either. A block that is never closed
  lasts until the end of the input. Only backtick fences count.
- The heading text is the rest of the line after the `#` characters, with
  spaces removed at both ends. If the text then ends with one or more `#`
  that directly follow a space, those `#` and the spaces before them are
  removed: `## Title ##` has the text `Title`, but `## C#` has the text
  `C#`. Every heading has some text left.

Numbering: keep a counter for each level 1 to 6, all starting at 0. For a
heading of level L, increase counter L by one and reset the counters of all
deeper levels to 0. The number of the heading is the counters 1 to L joined
by dots. So a level-3 heading directly after the first level-1 heading is
numbered `1.0.1`, and a document whose first heading has level 2 starts
with `0.1`.

Slugs: build the slug from the text in lower case: every space becomes a
`-`, letters `a`-`z`, digits and `-` are kept, every other character is
removed (`Usage & Tips!` gives `usage--tips`). If an earlier heading
already used this slug, append `-1`; if that is used as well, try `-2`, and
so on, taking the first one not used yet. The slug with its suffix then
counts as used.

Output: one line per heading, in document order: two spaces of indentation
for every level below level 1 (none for level 1, two spaces for level 2,
and so on), the number, a space, the text, a space and `(#slug)`.
