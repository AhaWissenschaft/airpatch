import sys

FIELDS = 7


def label(fields, home):
    title, first, last, street, postcode, city, country = fields
    if not (street or postcode or city):
        return None
    if first or last:
        name = " ".join(v for v in (title, first, last) if v)
    else:
        name = "To the occupant"
    lines = [name]
    if street:
        lines.append(street)
    place = " ".join(v for v in (postcode, city) if v)
    if place:
        lines.append(place)
    if country and country != home:
        lines.append(country.upper())
    return lines


def main():
    rows = sys.stdin.read().splitlines()
    home = rows[0].partition("=")[2].strip() if rows else ""
    labels = []
    for raw in rows[1:]:
        if not raw.strip():
            continue
        fields = [f.strip() for f in raw.split(";")]
        fields += [""] * (FIELDS - len(fields))
        lines = label(fields, home)
        if lines:
            labels.append("\n".join(lines))
    if labels:
        print("\n---\n".join(labels))


if __name__ == "__main__":
    main()
