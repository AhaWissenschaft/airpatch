# Live runs: calls, tokens, latency, error classes (descriptive)

## 8b

Run `20261005T082204Z-8b-benchmark`, served model(s): swiss-ai/Apertus-v1.5-8B; ledger: 236 calls, 299256 counted tokens, 0 overruns.

| condition | calls | errors | prompt tok | completion tok | total tok | latency median / p90 / max (s) | tries > 1 | verdicts | same as previous answer |
|---|---|---|---|---|---|---|---|---|---|
| C0 | 40 | 0 | 32347 | 11432 | 43779 | 2.0 / 2.8 / 4.1 | 0 | FAIL_TESTS 38, PASS 2 | - |
| C1 | 120 | 0 | 97041 | 34324 | 131365 | 1.9 / 2.8 / 4.0 | 0 | BUILD_ERROR 2, FAIL_TESTS 108, PASS 8, RESOURCE_LIMIT 1, TIMEOUT 1 | - |
| C2 | 76 | 0 | 102520 | 21592 | 124112 | 2.1 / 3.0 / 3.9 | 0 | FAIL_TESTS 76 | 64 / 76 |
| all | 236 | 0 | 231908 | 67348 | 299256 | 1.9 / 3.0 / 4.1 | 0 | BUILD_ERROR 2, FAIL_TESTS 222, PASS 10, RESOURCE_LIMIT 1, TIMEOUT 1 | 64 / 76 |

Finish reasons: {'stop': 236}. Failed hidden cases by reason (all model answers): {'wrong output': 1276, 'non-zero exit': 403, 'TIMEOUT': 10, 'output limit': 10}. Tokens per call: 1268; sum of call latencies: 7.8 min.

## 70b

Run `20261005T075518Z-19745-benchmark`, served model(s): swiss-ai/Apertus-v1.5-70B; ledger: 236 calls, 313667 counted tokens, 0 overruns.

| condition | calls | errors | prompt tok | completion tok | total tok | latency median / p90 / max (s) | tries > 1 | verdicts | same as previous answer |
|---|---|---|---|---|---|---|---|---|---|
| C0 | 40 | 0 | 32347 | 13262 | 45609 | 4.8 / 8.5 / 11.6 | 0 | FAIL_TESTS 38, PASS 2 | - |
| C1 | 120 | 0 | 97041 | 41100 | 138141 | 5.1 / 8.8 / 12.9 | 0 | BUILD_ERROR 2, FAIL_TESTS 111, PASS 6, RESOURCE_LIMIT 1 | - |
| C2 | 76 | 0 | 104340 | 25577 | 129917 | 5.0 / 9.1 / 10.3 | 0 | FAIL_TESTS 76 | 49 / 76 |
| all | 236 | 0 | 233728 | 79939 | 313667 | 5.0 / 9.0 / 12.9 | 0 | BUILD_ERROR 2, FAIL_TESTS 225, PASS 8, RESOURCE_LIMIT 1 | 49 / 76 |

Finish reasons: {'stop': 236}. Failed hidden cases by reason (all model answers): {'wrong output': 1181, 'non-zero exit': 368, 'memory limit': 2}. Tokens per call: 1329; sum of call latencies: 20.8 min.

