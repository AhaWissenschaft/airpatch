import sys


def main():
    grid = [line.rstrip("\n") for line in sys.stdin if line.strip()]
    rows, cols = len(grid), len(grid[0])
    start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "S")
    visited = set()

    def explore(r, c):
        """Steps from (r, c) to the nearest exit, or None if there is none."""
        if grid[r][c] == "E":
            return 0
        visited.add((r, c))
        best = None
        for dr, dc in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in visited:
                sub = explore(nr, nc)
                if sub is not None and (best is None or sub + 1 < best):
                    best = sub + 1
        return best

    steps = explore(*start)
    print("NO PATH" if steps is None else steps)


if __name__ == "__main__":
    main()
