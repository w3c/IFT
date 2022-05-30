import csv

print("<table>")
print("  <tr><th>Tag</th><th>Encoded As</th></tr>")
with open("feature-registry.csv") as r:
  reader = csv.reader(r, delimiter=",")
  i = 1
  for row in reader:
    if row[0] == "tag":
        continue
    v = "default" if row[2] == "1" else i
    if row[2] != "1":
        i += 1
    print(f"  <tr><td>{row[0]}</td><td>{v}</td></tr>")

print("</table>")
