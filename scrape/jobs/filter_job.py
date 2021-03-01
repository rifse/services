#!/usr/bin/env python3

import json
from pprint import pprint

with open('pretty.json', 'r') as inFile:
    data = json.load(inFile)

to_delete = []
matches = ['2020', 'tudentsk']
for number in data:
    description = data[number]['description']
    if any(x in description for x in matches):
        to_delete.append(number)

for number in to_delete:
    del data[number]

pprint(data)
