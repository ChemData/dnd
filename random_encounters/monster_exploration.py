import re
import pandas as pd
from mob_sets import FULL_MONSTERS

p = re.compile(r'DC [0-9]* [A-Z][a-z]*')
x = FULL_MONSTERS['bulette']
s = x.to_json_str()
names = []
dcs = []
stats = []
for name, monster in FULL_MONSTERS.items():
    string = monster.to_json_str()
    found_dcs = re.findall(p, string)
    if found_dcs is None:
        continue
    for new_dc in found_dcs:
        _, dc, stat = new_dc.split(' ')
        names += [name]
        dcs += [dc]
        stats += [stat]

output = pd.DataFrame({'mob': names, 'stat': stats, 'dc': dcs})