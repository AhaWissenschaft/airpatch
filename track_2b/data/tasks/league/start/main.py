import sys


def main():
    table = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        home, away, score = parts
        hg, ag = map(int, score.split("-"))
        for team in (home, away):
            table.setdefault(team, {"p": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0})
        table[home]["p"] += 1
        table[away]["p"] += 1
        table[home]["gf"] += hg
        table[home]["ga"] += ag
        table[away]["gf"] += ag
        table[away]["ga"] += hg
        if hg > ag:
            table[home]["w"] += 1
            table[away]["l"] += 1
        elif hg < ag:
            table[away]["w"] += 1
            table[home]["l"] += 1
        else:
            table[home]["d"] += 1
            table[away]["d"] += 1

    def points(t):
        return 3 * t["w"] + t["d"]

    order = sorted(table, key=lambda name: (-points(table[name]), name))
    for rank, name in enumerate(order, 1):
        t = table[name]
        print(f"{rank} {name} {t['p']} {t['w']} {t['d']} {t['l']} {t['gf']}:{t['ga']} {points(t)}")


if __name__ == "__main__":
    main()
