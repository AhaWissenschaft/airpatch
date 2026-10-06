import sys


def main():
    stats = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        home, away, score = parts
        hg, ag = map(int, score.split("-"))
        for team, gf, ga in ((home, hg, ag), (away, ag, hg)):
            s = stats.setdefault(team, [0, 0, 0, 0, 0, 0])
            s[0] += 1
            s[4] += gf
            s[5] += ga
            if gf > ga:
                s[1] += 1
            elif gf == ga:
                s[2] += 1
            else:
                s[3] += 1

    def points(s):
        return 3 * s[1] + s[2]

    def key(team):
        s = stats[team]
        return (-points(s), -(s[4] - s[5]), -s[4])

    order = sorted(stats, key=lambda t: (key(t), t))
    rank = 0
    for i, team in enumerate(order):
        if i == 0 or key(team) != key(order[i - 1]):
            rank = i + 1
        s = stats[team]
        print(f"{rank} {team} {s[0]} {s[1]} {s[2]} {s[3]} {s[4]}:{s[5]} {points(s)}")


if __name__ == "__main__":
    main()
