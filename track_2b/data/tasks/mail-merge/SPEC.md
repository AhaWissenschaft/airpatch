Prepare address labels from a list of address records.

The first line of standard input is `home=<country>`, the sender's own
country (spaces around the country name are ignored). Every following line
that is not empty (or only spaces) is one record with fields separated by
`;`:

`title;first name;last name;street;postcode;city;country`

- Spaces around each field are removed; spaces inside a field are kept.
- A record may have fewer than seven fields; the missing trailing fields
  are empty. Any field may be empty. A record never has more than seven
  fields.

Each record becomes a label of up to four lines, in this order:

1. The name line: the non-empty values among title, first name and last
   name, joined by single spaces. If the first name and the last name are
   both empty, the name line is `To the occupant` instead (the title is then
   not used).
2. The street, if it is not empty.
3. The non-empty values among postcode and city, joined by a single space;
   this line is left out if both are empty.
4. The country in upper case; left out if the country is empty or equal to
   the home country when upper/lower case is ignored.

A record whose street, postcode and city are all empty cannot be delivered
and produces no label at all.

Print the labels in input order with a line containing exactly `---` between
two consecutive labels (not before the first label and not after the last
one). Print nothing if there is no label.
