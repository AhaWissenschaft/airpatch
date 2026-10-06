The first line of standard input is the line width `W` (an integer, at least 1).
The rest of the input is text.

Split the text into words (separated by any whitespace, including line
breaks) and print them greedily as lines of at most `W` characters: put as
many words on a line as fit, separated by single spaces, then start a new
line. A word longer than `W` is printed on a line of its own and is not
split. Print nothing if the text has no words.
