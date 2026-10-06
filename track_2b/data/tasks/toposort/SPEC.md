Each non-empty line of standard input has the form `task: dep1 dep2 ...`,
meaning that `task` can only be done after all the listed dependencies are
done. The list may be empty (`task:`). Spaces around names are ignored; names
contain no spaces and no colons.

- A task may appear on several lines; its dependencies are then all
  dependencies listed on those lines.
- A dependency listed more than once counts once.
- Every name that appears anywhere (before or after a colon) is a task.

Print a work order, one task per line, built like this: repeatedly pick, among
all tasks not yet done whose dependencies are all done, the one with the
smallest name in plain character order (upper-case letters before lower-case
letters), print it and mark it as done.

If at some point tasks remain but none of them can be picked (because of a
circular dependency, including a task that depends on itself), print a last
line `CYCLE: ` followed by all remaining tasks in sorted order, separated by
single spaces. Empty input gives no output.
