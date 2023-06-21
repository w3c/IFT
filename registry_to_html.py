import csv
import re

print("<table>")
print("  <tr><th>Tag</th><th>Encoded As</th><th>Encode If</th><th>Encoding Version</th></tr>")
with open("feature-registry.csv") as r:
  reader = csv.reader(r, delimiter=",")
  lines = [row for row in reader]

  i = 1
  for is_default in [True, False]:
    version = 1
    for row in lines:
      if row[0].startswith("VERSION_2"):
        version = 2
        continue

      if row[0] == "Tag" or row[0].startswith("#"):
        continue

      if is_default != (int(row[2]) == 1):
        continue

      presence = "not needed" if int(row[2]) == 1 else "needed"
      m = re.search("[a-z]{2}([0-9]{2})-[a-z]{2}([0-9]{2})", row[0])
      if m:
        start = i
        end = i + (int(m.group(2)) - int(m.group(1)))
        i += end - start + 1
        v = f"{start}-{end}"
      else:
        v = i
        i += 1

      print(f"  <tr><td>{row[0]}</td><td>{v}</td><td>{presence}</td><td>{version}</td></tr>")

print("</table>")
