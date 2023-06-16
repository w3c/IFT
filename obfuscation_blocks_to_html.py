import csv
import re
import requests

r = requests.get('https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt')
lines = r.text.split("\n")
lines = [line for line in lines if line and not line.startswith("#")]

BLOCKS_TO_INCLUDE_REGEX = [
    r"CJK Unified Ideographs.*",
]

print("<table>")
print("  <thead>")
print("    <tr>")
print("      <th>Unicode Block Name</th>")
print("      <th>Codepoint Range</th>")
print("    </tr>")
print("  </thead>")
print("  <tbody>")

for line in lines:
  parts = line.split("; ")

  block = parts[0]
  name = parts[1]

  keep = False
  for regex in BLOCKS_TO_INCLUDE_REGEX:
    if re.search(regex, name):
      keep = True
      break

  if not keep:
    continue

  print("    <tr>")
  print(f"      <td>{name}</td>")
  print(f"      <td>{block}</td>")
  print("    </tr>")

print("  </tbody>")
print("</table>")
