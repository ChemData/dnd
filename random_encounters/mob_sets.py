from json import load, loads, dump, dumps
import os
from utils import to_numeric_cr


MOB_SETS = {
    "wolves": ["wolf", "dire wolf", 'mastiff'],
    "bears": ["black bear", "brown bear", "cave bear"],
    "millipedes": ["giant millipede", "adult giant millipede", "giant centipede", "swarm of centipedes"],
    "bandits": ["bandit", "bandit captain", "veteran", "knight", "scout", "gladiator", "druid", "spy"],
    "dwarves": ["orc war chief", "hobgoblin captain", "hobgoblin warlord", "mage", "veteran", "priest", "berserker",
                "duergar", "scout"],
    "thri-kreen": ["thri-kreen"],
    "sahuagin": ["sahuagin", "sahuagin baron", "sahuagin priestess", 'giant sea horse', 'reef shark'],
    "coastal_elementals": ["air elemental", "ice mephit", "water elemental", "water weird", "marid", "mud mephit"],
    "land_elementals": ["dao", "dust mephit", "galeb duhr", "gargoyle", "mud mephit", "xorn", "earth elemental"],
    "mountain_elementals": ["galeb duhr", "gargoyle", "dust mephit", "air elemental", "earth elemental"],
    "fire_elementals": ["smoke mephit", "steam mephit", "magma mephit", "magmin", "fire elemental", "fire snake"],
    "forest_creatures": ["giant weasel", "boar", "elk", "giant badger", "giant goat", "giant elk"],
    "reptiles": ["lizard", "flying snake", "poisonous snake", "constrictor snake", "giant lizard",
                 "giant poisonous snake", "crocodile", "giant constrictor snake", "swarm of poisonous snakes",
                 "giant crocodile"],
    "rhinos": ['rhinoceros', 'draft horse', 'triceratops'],
    "ankhegs": ['ankheg', 'ankheg tunneler', 'ankheg worker', 'ankheg queen'],
    "boars": ['boar', 'giant boar', 'badger'],
    "ogres": ['half-ogre (ogrillon)', 'ogre', 'giant hyena', 'hyena', "boulder thrower", "cyclops"],
    "harpies": ['harpy', 'blood hawk', 'axe beak', 'giant owl', 'cockatrice', 'giant eagle', 'wingmistress'],
    "spiders": ['swarm of spiders', 'giant wolf spider', 'spider', 'giant spider', 'phase spider'],
    "vampires": ['vampire spawn', 'vampire', 'vampire spellcaster', 'vampire warrior'],
    "cultists": ['cultist', 'priest', 'mage', 'cult fanatic', 'acolyte', 'archmage', 'guard'],
    "satyrs": ['satyr', 'goat', 'giant goat', 'swarm of wasps', "satyr marksman", "satyr charger"],
    "kuo-toas": ['kuo-toa', 'kuo-toa whip', 'kuo-toa monitor', 'kuo-toa archpriest', 'giant crab', 'crocodile'],
    "centaurs": ["centaur"],
    "hyenas": ["jackal", "hyena", "giant hyena"]
}

ENVIRONMENT_SETS = {
    "southern_forest": [
        "wolves", "bears", "millipedes", "bandits", "forest_creatures", "boars", "ogres", "harpies", "spiders",
        "satyrs"],
    "southern_shore": [
        "kuo-toas", "coastal_elementals", "sahuagin", "bandits", "ogres"
    ],
    "southern_plains": [
        "wolves", "bandits", "rhinos", "boars", "millipedes", "land_elementals", "reptiles", 'ankhegs', 'hyenas'
    ]
    }


XP_AMOUNTS = {
    '0':10, '1/8':25, '1/4':50, '1/2':100, '1':200, '2':450, '3':700, '4':1100, '5': 1800, '6': 2300,
    '7': 2900, '8':3900, '9': 5000, '10': 5900, '11': 7200, '12': 8400, '13': 10000, '14': 11500, '15': 13000,
    '16': 15000, '17': 18000, '18': 20000, '19': 22000, '20': 25000}


def load_monsters():
    if not os.path.exists('monsters.json'):
        cleanup_downloaded_json()
    with open('monsters.json', 'r') as f:
        output = load(f)

    with open('homebrew_monsters.json', 'r') as f:
        monsters = load(f)
    for _, monster_data in monsters.items():
        output[monster_data['Name']] = monster_data

    return output


def cleanup_downloaded_json():
    with open('Monster Manual.JSON', 'r', encoding='utf8') as f:
        monsters = load(f)
    output = {}
    for _, monster_data in monsters.items():
        monster = loads(monster_data)
        if type(monster) == list:
            continue
        monster['CR'] = monster['Challenge']
        del monster['Challenge']
        monster['Name'] = monster['Name'].lower()
        monster['size'] = monster['Type'].split(' ')[0].lower()
        monster['category'] = monster['Type'].split(',')[0].split(' ')[1]
        monster['alignment'] = monster['Type'].split(',')[-1]
        output[monster['Name']] = monster
    with open('monsters.json', 'w') as f:
        dump(output, f, indent=4)


class FullMob:
    def __init__(self, stat_block):
        self.stat_block = stat_block

    @property
    def ac(self):
        return self.stat_block['AC']['Value']

    def set_ac(self, new_ac):
        self.stat_block['AC']['Value'] = new_ac

    @property
    def hp(self):
        return self.stat_block['HP']['Value'], self.stat_block['HP']['Notes']

    def set_hp(self, fixed_hp: int, hp_roll: str):
        if hp_roll[0] != '(':
            hp_roll = f'({hp_roll})'
        self.stat_block['HP']['Value'] = fixed_hp
        self.stat_block['HP']['Notes'] = hp_roll

    @property
    def cr(self):
        return self.stat_block['CR']

    def set_cr(self, new_cr: str):
        new_cr = str(new_cr)
        self.stat_block['CR'] = new_cr

    @property
    def size(self):
        return self.stat_block['size']

    def set_size(self, new_size: str):
        self.stat_block['size'] = new_size

    def to_json_str(self):
        return dumps(self.stat_block)

    def add_to_homebrew(self):
        with open('homebrew_monsters.json', 'r') as f:
            hb = load(f)
        hb[self.stat_block['Id']] = self.stat_block
        with open('homebrew_monsters.json', 'w') as f:
            dump(hb, f, indent=4)

    def to_homebrewery(self):
        b = self.stat_block
        output = "{{monster,frame,wide\n"
        output += f"## {b['Name'].capitalize()}\n"
        output += f"*{b['Type']}*\n___\n"
        output += f"**Armor Class** :: {b['AC']['Value']}"
        if b['AC']['Notes'] != "":
            output += f" {b['AC']['Notes']}"
        output += f"\n**Hit Points**  :: {b['HP']['Value']}{b['HP']['Notes']}\n"
        output += f"**Speed**  :: {', '.join(b['Speed'])}\n___\n"
        output += "| STR | DEX | CON | INT | WIS | CHA |\n|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|\n"
        output += f"|{self.stat_to_modifier(b['Abilities']['Str'])}|{self.stat_to_modifier(b['Abilities']['Dex'])}|" \
                  f"{self.stat_to_modifier(b['Abilities']['Con'])}|{self.stat_to_modifier(b['Abilities']['Int'])}|" \
                  f"{self.stat_to_modifier(b['Abilities']['Wis'])}|{self.stat_to_modifier(b['Abilities']['Cha'])}|\n___\n"
        if len(b['Saves']) > 0:
            output += f"**Saves** :: {', '.join([s['Name'] + ' +' + str(s['Modifier']) for s in b['Saves']])}\n"
        if len(b['Skills']) > 0:
            output += f"**Skills** :: {', '.join([s['Name'] + ' +' + str(s['Modifier']) for s in b['Skills']])}\n"
        if len(b['DamageVulnerabilities']) > 0:
            output += f"**Vulnerabilities** :: {', '.join(b['DamageVulnerabilities'])}\n"
        if len(b['DamageResistances']) > 0:
            output += f"**Damage Resistances** :: {', '.join(b['DamageResistances'])}"
        if len(b['DamageImmunities']) > 0:
            output += f"**Damage Immunities** :: {', '.join(b['DamageImmunities'])}\n"
        if len(b['ConditionImmunities']) > 0:
            output += f"**Condition Immunities** :: {', '.join(b['ConditionImmunities'])}\n"
        if len(b['Senses']) > 0:
            output += f"**Senses** :: {', '.join(b['Senses'])}\n"
        if len(b['Languages']) > 0:
            output += f"**Languages** :: {', '.join(b['Languages'])}\n"
        output += f"**Challenge** :: {b['CR']} ({XP_AMOUNTS[b['CR']]} XP)\n___\n"
        output += ':\n'.join([f"***{trait['Name']}.*** {trait['Content']}\n" for trait in b['Traits']])

        if len(b['Actions']) > 0:
            output += "### Actions\n"
            output += ':\n'.join([f"***{action['Name']}.*** {action['Content']}\n" for action in b['Actions']])
        if len(b['Reactions']) > 0:
            output += "### Reactions\n"
            output += ':\n'.join([f"***{reaction['Name']}.*** {reaction['Content']}\n" for reaction in b['Reactions']])
        if len(b['LegendaryActions']) > 0:
            output += "### Legendary Actions\n"
            output += ':\n'.join([f"***{action['Name']}.*** {action['Content']}\n" for action in b['LegendaryActions']])
        output += "}}"
        return output

    def stat_to_modifier(self, val):
        mod = (val-10)//2
        return f"{val}({'+' if mod >= 0 else ''}{mod})"


class Mob:
    def __init__(self, Name, CR, **kwargs):
        self.name = Name
        self.cr = str(CR)
        self.num_cr = to_numeric_cr(CR)
        self.xp = XP_AMOUNTS[str(CR)]

    def __repr__(self):
        return f"{self.name}(cr {self.cr})"

    def __hash__(self):
        return hash(f'{self.name}{self.cr}')

    def __eq__(self, other):
        if self.name == other.name and self.cr == other.cr:
            return True
        return False


MONSTERS = load_monsters()
FULL_MONSTERS = {x: FullMob(v) for x, v in MONSTERS.items()}
for set_name, mob_names in MOB_SETS.items():
    MOB_SETS[set_name] = [Mob(**MONSTERS[x]) for x in mob_names]
