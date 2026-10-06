import sys


def main():
    lines = sys.stdin.read().splitlines()
    home = lines[0].split("=")[1]
    for raw in lines[1:]:
        if not raw.strip():
            continue
        title, first, last, street, postcode, city, country = raw.split(";")
        print(f"{title} {first} {last}".strip())
        print(street)
        print(f"{postcode} {city}")
        if country != home:
            print(country.upper())
        print("---")


if __name__ == "__main__":
    main()
