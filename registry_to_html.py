import csv
import re

print("<table>")
print("  <tr><th>Tag</th><th>Encoded As</th></tr>")
with open("feature-registry.csv") as r:
  reader = csv.reader(r, delimiter=",")
  i = 1
  for row in reader:
    if row[0] == "tag" or row[0].startswith("#"):
        continue


    if row[2] == "1":
      v = "default"
    else:
      m = re.search("[a-z]{2}([0-9]{2})-[a-z]{2}([0-9]{2})", row[0])
      if m:
        start = i
        end = i + (int(m.group(2)) - int(m.group(1)))
        i += end - start + 1
        v = f"{start}-{end}"
      else:
        v = i
        i += 1

    print(f"  <tr><td>{row[0]}</td><td>{v}</td></tr>")

print("</table>")
