The first line of standard input is the capacity `C` of a cache (an
integer, at least 1). Every following non-empty line is one command:

- `put <key> <value>`: store `value` under `key`. If the key is already in the
  cache, its value is replaced. If the key is new and the cache already holds
  `C` keys, first remove the least recently used key and print
  `evict <key>`.
- `get <key>`: print the value stored under `key`, or `miss` if the key is
  not in the cache.
- `dump`: print all keys in the cache on one line, from the most recently used
  to the least recently used, separated by single spaces; print `empty` if
  the cache holds no keys.

A key counts as used when it is stored by `put` (new or replaced) and when a
`get` finds it. A `get` that misses and a `dump` change nothing. Keys and
values are words without spaces.
