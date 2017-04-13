#!/usr/bin/env python3

content = []
with open('foo', 'r') as fh:
    for line in fh:
        line = line.strip()

        if line.endswith("]',"):
            line = line.replace("'parent", "parent")
            line = line.replace("]',", "],")
        content.append(line)


content = ' '.join(content)
content = content.replace("'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x',", "'xxxxxxxx',")
content = content.replace("'x', 'x', 'x', 'x', 'x', 'x', 'x',",      "'xxxxxxx',")
content = content.replace("'x', 'x', 'x', 'x', 'x', 'x',",           "'xxxxxx',")
content = content.replace("'x', 'x', 'x', 'x', 'x',",                "'xxxxx',")
content = content.replace("'x', 'x', 'x', 'x',",                     "'xxxx',")
content = content.replace("'x', 'x', 'x',",                          "'xxx',")
content = content.replace("'x', 'x',",                               "'xx',")

print(content)
