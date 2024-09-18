import csv
import re

print("<table>")
print("  <tr><th>Tag</th><th>Name</th></tr>")
with open("feature-registry.csv") as r:
  reader = csv.reader(r, delimiter=",")
  lines = [row for row in reader]

  for row in lines:
    if row[0] == "Tag" or row[0].startswith("#"):
      continue

    if int(row[2]) != 1:
      continue

    print(f"  <tr><td>{row[0]}</td><td>{row[1]}</td></tr>")

print("</table>")
