import pandas as pd
import math
import random
import warnings
import re
from copy import deepcopy
from typing import Optional
from mob_sets import FULL_MONSTERS, FullMob



STAT_TABLE = pd.read_csv('generic_stats.csv', index_col=0)
STAT_TABLE['pos index'] = range(len(STAT_TABLE))
STAT_TABLE['Prof Bonus low'] = STAT_TABLE['Prof Bonus']
STAT_TABLE['Prof Bonus high'] = STAT_TABLE['Prof Bonus']
STAT_TABLE['DC low'] = STAT_TABLE['DC']
STAT_TABLE['DC high'] = STAT_TABLE['DC']

CRS = tuple(['0', '1/8', '1/4', '1/2'] + [str(x) for x in range(1,21)])


def shift_cr(cr: str, amount: int):
    cr = str(cr)
    start_index = CRS.index(cr)
    end_index = start_index + amount
    if end_index < 0:
        return 0, -1
    if end_index >= len(CRS):
        return CRS[-1], 1
    return CRS[end_index], 0


def cr_offset(stat, value, current_cr):
    current_cr = str(current_cr)
    expected_index = STAT_TABLE.loc[current_cr, 'pos index']
    possible_cr = STAT_TABLE[(STAT_TABLE[f'{stat} low'] <= value) & (STAT_TABLE[f'{stat} high'] >= value)].copy()
    possible_cr['diff'] = possible_cr['pos index'] - expected_index
    possible_cr['abs diff'] = possible_cr['diff'].apply(abs)
    closest_cr = possible_cr.loc[possible_cr['abs diff'] == possible_cr['abs diff'].min()].iloc[0]

    cr_diff = closest_cr['diff']
    if closest_cr[f'{stat} high'] - closest_cr[f'{stat} low'] == 0:
        frac = 0
    else:
        frac = (value - closest_cr[f'{stat} low'])/(closest_cr[f'{stat} high'] - closest_cr[f'{stat} low'])

    return cr_diff, frac


def generate_value(stat, cr, frac=0):
    cr = str(cr)
    return round(STAT_TABLE.loc[cr, f'{stat} low'] + frac * (
            STAT_TABLE.loc[cr, f'{stat} high'] - STAT_TABLE.loc[cr, f'{stat} low']))


def generate_hp(cr, frac, size):
    target_hp = generate_value('HP', cr, frac)
    hit_dice = {
        'tiny': (4, 2.5), 'small': (6, 3.5), 'medium': (8, 4.5), 'large': (10, 5.5), 'huge': (12, 6.5),
        'gargantuan': (20, 10.5)}
    hit_die = hit_dice[size]
    return dice_from_hp(target_hp, hit_die[1])


def dice_from_hp(target_hp: int, hit_die: int):
    ave_value = hit_die/2 + 0.5
    n_dice = int(target_hp // ave_value)
    make_fixed = random.choice(range(0, max(1, n_dice-4)))
    n_dice -= make_fixed
    fixed = round((target_hp-make_fixed*ave_value) % ave_value+make_fixed*ave_value)
    return target_hp, f'{n_dice}d{hit_die}+{fixed}'


def scale_monster(monster: FullMob, new_cr: str, new_size: Optional[str] = None):
    new_cr = str(new_cr)
    new_monster = deepcopy(monster)
    old_cr = monster.cr
    if new_size is None:
        new_size = monster.size
    new_monster.stat_block['Source'] = 'DSO Homebrew'
    new_monster.stat_block['size'] = new_size
    new_monster.stat_block['Version'] = ""
    new_monster.stat_block['Type'] = f"{new_size} {new_monster.stat_block['category']}, {new_monster.stat_block['alignment']}"

    new_monster.set_cr(new_cr)
    new_name = input('What is the monster\'s name? ')
    new_monster.stat_block['Name'] = new_name
    new_monster.stat_block['Id'] = new_name.replace(' ', '_')
    old_to_hit = int(input('What is the monster\'s current to hit? '))
    old_damage = int(input('What is the monster\'s current damage per round? '))
    old_dc = input('What is the monster\'s current save DC for abilities? ')

    # Set HP
    cr_offset_amount, cr_frac = cr_offset('HP', monster.hp[0], old_cr)

    new_stat_cr, shift_flag = shift_cr(new_cr, cr_offset_amount)
    if shift_flag == -1:
        warnings.warn('The scaled monster should have HP CR of below 0. Its HP has been set to CR 0 which might make it '
                      'stronger than expected.')
    if shift_flag == 1:
        warnings.warn('The scaled monster should have HP CR of above 20. Its HP has been set to CR 20 which might make it '
                      'weaker than expected.')
    new_hp = generate_hp(new_stat_cr, cr_frac, new_size)
    new_monster.set_hp(*new_hp)
    print(f'Suggested HP: {new_hp[0]}({new_hp[1]})')

    # Set AC
    cr_offset_amount, cr_frac = cr_offset('AC', monster.ac, old_cr)

    new_stat_cr, shift_flag = shift_cr(new_cr, cr_offset_amount)
    if shift_flag == -1:
        warnings.warn(
            'The scaled monster should have AC CR of below 0. Its AC has been set to CR 0 which might make it '
            'stronger than expected.')
    if shift_flag == 1:
        warnings.warn(
            'The scaled monster should have AC CR of above 20. Its AC has been set to CR 20 which might make it '
            'weaker than expected.')
    new_ac = generate_value('AC', new_stat_cr, cr_frac)
    new_monster.set_ac(new_ac)
    print(f'Suggested AC: {new_ac}')

    # Print the suggested new to hit
    cr_offset_amount, cr_frac = cr_offset('Hit', old_to_hit, old_cr)

    new_stat_cr, shift_flag = shift_cr(new_cr, cr_offset_amount)
    if shift_flag == -1:
        warnings.warn(
            'The scaled monster should have To Hit CR of below 0. Its To Hit has been set to CR 0 which might make it '
            'stronger than expected.')
    if shift_flag == 1:
        warnings.warn(
            'The scaled monster should have To Hit CR of above 20. Its To Hit has been set to CR 20 which might make it '
            'weaker than expected.')
    print(f'Suggested To Hit: +{generate_value("Hit", new_stat_cr, cr_frac)}')

    # Print the suggested new damage
    cr_offset_amount, cr_frac = cr_offset('Damage', old_damage, old_cr)

    new_stat_cr, shift_flag = shift_cr(new_cr, cr_offset_amount)
    if shift_flag == -1:
        warnings.warn(
            'The scaled monster should have Damage CR of below 0. Its Damage has been set to CR 0 which might make it '
            'stronger than expected.')
    if shift_flag == 1:
        warnings.warn(
            'The scaled monster should have To Damage of above 20. Its Damage has been set to CR 20 which might make it '
            'weaker than expected.')
    print(f'Suggested Damage per turn: {generate_value("Damage", new_stat_cr, cr_frac)}')

    # Print the suggested new DC
    if old_dc != '':
        cr_offset_amount, cr_frac = cr_offset('DC', old_dc, old_cr)

        new_stat_cr, shift_flag = shift_cr(new_cr, cr_offset_amount)
        if shift_flag == -1:
            warnings.warn(
                'The scaled monster should have DC CR of below 0. Its DC has been set to CR 0 which might make it '
                'stronger than expected.')
        if shift_flag == 1:
            warnings.warn(
                'The scaled monster should have To DC of above 20. Its DC has been set to CR 20 which might make it '
                'weaker than expected.')
        print(f'Suggested DC: {generate_value("DC", new_stat_cr, cr_frac)}')
    return new_monster


x = FULL_MONSTERS['ankheg']

#t = scale_monster(x, '6', 'huge')
#h = t.to_homebrewery()
#print(h)