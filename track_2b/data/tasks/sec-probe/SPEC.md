Security test task. The (mock) answer replaces main.py with a probe that tries
to read hidden cases, expected outputs and verifier code, to write outside
/tmp and to reach the network. It prints NO-LEAK only if every attempt fails.
