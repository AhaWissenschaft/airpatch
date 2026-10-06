"""Small, dependency-free statistics for solved-task counts."""

from __future__ import annotations

from math import comb, sqrt

Z95 = 1.959963984540054


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """95% Wilson score interval for a proportion k/n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(only_a: int, only_b: int) -> float:
    """Two-sided exact McNemar p-value from the discordant pair counts."""
    n = only_a + only_b
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(min(only_a, only_b) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired(a: dict[str, bool], b: dict[str, bool]) -> dict:
    """Compare two conditions on the tasks both were run on."""
    tasks = sorted(set(a) & set(b))
    only_a = sum(a[t] and not b[t] for t in tasks)
    only_b = sum(b[t] and not a[t] for t in tasks)
    return {"tasks": len(tasks), "both": sum(a[t] and b[t] for t in tasks), "only_a": only_a,
            "only_b": only_b, "neither": sum(not a[t] and not b[t] for t in tasks),
            "p_value": mcnemar_exact(only_a, only_b)}
