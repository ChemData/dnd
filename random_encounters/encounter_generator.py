from copy import deepcopy, copy
from typing import Union, List, Optional, Tuple, Dict
from random import shuffle, choice, choices
import warnings
import numpy as np
import pyperclip
import pandas as pd
from mob_sets import MOB_SETS, MONSTERS, Mob, ENVIRONMENT_SETS
from utils import to_numeric_cr


NUMBER_MULTIPLIER = {1: 1, 2:1.5, 3:2, 4:2, 5:2, 6:2, 7:2.5, 8:2.5, 9:2.5, 10:2.5, 11:3, 12:3, 13:3, 14:3, 15:4}
DIFFICULTY_TABLE = pd.DataFrame(
    {'easy': [25, 50, 75, 125, 250, 300, 350, 450, 550, 600, 800, 1000, 1100, 1250, 1400, 1600, 2000, 2100, 2400, 2800],
     'medium': [50, 100, 150, 250, 500, 600, 750, 900, 1100, 1200, 1600, 2000, 2200, 2500, 2800, 3200, 3900, 4200, 4900, 5700],
     'hard': [75, 150, 225, 375, 750, 900, 1100, 1400, 1600, 1900, 2400, 3000, 3400, 3800, 4300, 4800, 5900, 6300, 7300, 8500],
     'deadly': [100, 200, 400, 500, 1100, 1400, 1700, 2100, 2400, 2800, 3600, 4500, 5100, 5700, 6400, 7200, 8800, 9500, 10900, 12700]},
    index=range(1, 21)
)


def bold(text: str):
    return '\033[1m' + text + '\033[0m'


class Group:

    def __init__(self, mobs: Optional[List[Mob]] = None):
        self.mobs = []
        self.xp_total = 0
        if mobs is not None:
            self.add(mobs)

    def __repr__(self):
        if len(self) == 0:
            return 'Group()'
        mob_count = count_values(self.mobs)
        output = 'Group('
        for mob, count in mob_count.items():
            if count > 1:
                output += f'{count}x'
            output += f'{mob}, '
        output = output[:-2] + f')[{self.xp_total}]'
        return output

    def simple_repr(self):
        mob_count = count_values(self.mobs)
        output = ''
        for mob, count in mob_count.items():
            output += f'{count} '
            output += f'{bold(mob.name.capitalize())}'
            if count > 1:
                output += bold('s')
            output += ', '
        output = output[:-2]
        return output

    def add(self, new_mobs: Union[Mob, List[Mob]]):
        if type(new_mobs) == Mob:
            new_mobs = [new_mobs]
        self.mobs += new_mobs
        self.xp_total = sum([mob.xp for mob in self.mobs]) * NUMBER_MULTIPLIER.get(len(self.mobs), 4)
        self.mobs.sort(key=lambda mob: mob.num_cr, reverse=True)

    def __eq__(self, other):
        if tuple(self.mobs) == tuple(other.mobs):
            return True
        return False

    def __hash__(self):
        return hash(tuple(self.mobs))

    def __getitem__(self, index):
        return self.mobs[index]

    def __len__(self):
        return len(self.mobs)


# Need a function that just generates a single group with the desired characteristics

def unique_group(
        mobs: List[Mob],
        party: List[int],
        difficulty: str,
        max_num: int = 20,
        min_cr: Optional[str] = None,
        existing_groups: Optional[List[Group]] = None) -> (List[Group], int):
    """Generate a single Group of Mobs that fits the desired characteristics and is different from
        other provided Groups."""
    if existing_groups is None:
        existing_groups = set()
    else:
        existing_groups = set(existing_groups)
    min_val, max_val = difficulty_range(party, difficulty)
    if min_cr is not None:
        mobs = [mob for mob in mobs if mob.num_cr >= to_numeric_cr(min_cr)]
    redundant_generations = 0
    while redundant_generations < 10:
        new_group = add_mobs(Group(), mobs, min_val, max_val, max_num)
        if new_group not in existing_groups:
            return new_group
        redundant_generations += 1
    raise NoUniqueGroup


def add_mobs(group: Group, mobs: List[Mob], min_val, max_val, max_num: Optional[int]=None):
    if max_num is not None and len(group) >= max_num:
        raise NoLegalGroups
    options = copy(mobs)
    if group.xp_total >= min_val:
        options += [None]
    shuffle(options)
    for pick in options:
        if pick is None:
            return group
        new_group = deepcopy(group)
        new_group.add(pick)
        if new_group.xp_total > max_val:
            continue
        else:
            try:
                complete_group = add_mobs(new_group, mobs, min_val, max_val, max_num)
                return complete_group
            except NoLegalGroups:
                continue
    raise NoLegalGroups


class NoLegalGroups(Exception):

    def __init__(self):
        pass


class NoUniqueGroup(Exception):

    def __init__(self):
        pass


def enumerate_groups(
        mobs: List[Mob],
        party: List[int],
        difficulty: str,
        max_num: int = 20,
        min_cr: Optional[str] = None) -> List[Group]:
    xp_lower_limit, xp_upper_limit = difficulty_range(party, difficulty)
    if min_cr is not None:
        mobs = [mob for mob in mobs if mob.num_cr >= to_numeric_cr(min_cr)]

    active = {Group()}
    finished = set()
    while len(active) > 0:
        add_to = active.pop()
        for mob in mobs:
            new = deepcopy(add_to)
            new.add(copy(mob))
            if xp_lower_limit <= new.xp_total <= xp_upper_limit and new not in finished:
                finished.add(new)
            if new.xp_total < xp_upper_limit and new not in active:
                if max_num is None or len(new.mobs) < max_num:
                    active.add(new)
    finished = list(finished)
    finished.sort(key=lambda x: x.xp_total, reverse=True)
    return finished


def difficulty_range(party: List[int], difficulty: str) -> (float, float):
    """Return the lower and upper """
    xp_lower_limit = DIFFICULTY_TABLE.loc[party, difficulty].sum()
    if difficulty == 'easy':
        xp_upper_limit = DIFFICULTY_TABLE.loc[party, 'medium'].sum()
    if difficulty == 'medium':
        xp_upper_limit = DIFFICULTY_TABLE.loc[party, 'hard'].sum()
    if difficulty == 'hard':
        xp_upper_limit = DIFFICULTY_TABLE.loc[party, 'deadly'].sum()
    if difficulty == 'deadly':
        xp_upper_limit = xp_lower_limit * 1.6
    xp_upper_limit -= 1
    return xp_lower_limit, xp_upper_limit


def count_values(list_to_count):
    output = {}
    for v in list_to_count:
        output[v] = output.get(v, 0) + 1
    return output


def make_roll_table(
        mob_sets: Dict[str, List[Mob]],
        party: List[int],
        max_mobs: Optional[int],
        min_cr: Optional[str] = None,
        difficulties: Tuple[Tuple[str, int], ...] = (('easy', 3), ('medium', 3), ('hard', 2), ('deadly', 2)),
        start_roll: int = 1):
    output = []
    genned_groups = []
    for difficulty, number in difficulties:
        successful = 0
        usable_sets = list(mob_sets.keys())
        while successful < number:
            if len(usable_sets) == 0:
                raise ValueError(
                    f"There are no sets of mobs able to generate a unique, legal, {difficulty} set. {len(genned_groups)}"
                    f" groups were successfully made before this")
            mob_set_name = choice(usable_sets)
            try:
                new_group = unique_group(mob_sets[mob_set_name], party, difficulty, max_mobs, min_cr, genned_groups)
                genned_groups += [new_group]
                output += [(new_group, difficulty, mob_set_name)]
                successful += 1
            except NoUniqueGroup:
                warnings.warn(f'It was not possible to generate a unique {difficulty} group for {mob_set_name}.')
                usable_sets.remove(mob_set_name)
    """
    if start_roll == 1:
        print('Roll\tEncounter\tDifficulty\tTheme')
    c = start_roll
    for group, difficulty, set_name in output:
        print(f'{c}\t{group.simple_repr()}\t{difficulty.capitalize()}\t{set_name.capitalize()}')
        c += 1"""
    return output


def format_roll_table_for_homebrewery(table: List, table_name: str, table_start: int = 1):
    output = f"{{{{wide\n##### {table_name}\n"
    output += "| Roll | Encounter | Difficulty | Theme |\n|:---|:---------------------:|:-------:|:-------:|\n"
    for row in table:
        output += f"|{table_start}\t|{row[0].simple_repr()}\t|{row[1].capitalize()}\t|{row[2].capitalize()}\t|\n"
        table_start += 1
    output += "}}\n"
    return output


def combat_difficulty(party: List[int], mob_set):
    if type(mob_set[0]) == int or type(mob_set[0]) == str:
        mob_set = Group([Mob(f'cr{x}', x) for x in mob_set])
    for difficulty in ['easy', 'medium', 'hard', 'deadly']:
        low_xp, high_xp = difficulty_range(party, difficulty)
        if difficulty == 'easy' and mob_set.xp_total < low_xp:
            return 'so easy'
        if low_xp <= mob_set.xp_total <= high_xp:
            return difficulty
    return 'beyond deadly'
