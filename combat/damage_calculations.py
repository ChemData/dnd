import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time


class Monster:

    def __init__(self, name, ac, hp, speed, dc, str, dex, con, int, wis, cha):
        self.name = name
        self.ac = ac
        self.hp = hp
        self.speed = speed
        self.dc = dc
        self.str = str
        self.dex = dex
        self.con = con
        self.int = int
        self.wis = wis
        self.cha = cha


def roll_damage(roll, as_prob=True):
    """
    2d6 = roll two d6
    2d4+3 = roll two d4 and add 3
    :param roll:
    :return:
    """
    count, size = roll.split("d")
    count = int(count)
    size = size.split("+")
    if len(size) == 1:
        fixed = 0
    else:
        fixed = int(size[1])
    size = int(size[0])
    rolls = np.random.randint(1, size+1, (10000, count)).sum(axis=1) + fixed

    if as_prob:
        return np.bincount(rolls)/len(rolls)

    return rolls


def single_roll(roll):
    count, size = roll.split("d")
    count = int(count)
    size = size.split("+")
    if len(size) == 1:
        fixed = 0
    else:
        fixed = int(size[1])
    size = int(size[0])
    return np.random.randint(1, size+1, count).sum() + fixed


def integer_hist(data):
    plt.hist(data, bins=np.arange(data.min()-1, data.max()+2), align="left")


def attack(to_hit, AC):
    repeats = 10000
    rolls = np.random.randint(1, 21, repeats)
    rolls[rolls == 1] = -1000
    rolls[rolls == 20] = 1000
    rolls += to_hit
    hits = (rolls >= AC).sum()
    return hits/repeats


def spell(DC, target_modifier):
    repeats = 10000
    rolls = np.random.randint(1, 21, repeats) + target_modifier
    hits = (rolls < DC).sum()
    return hits/repeats


def damage_distribution(hit_probability, damage_dice, half_on_fail=False):
    probs = roll_damage(damage_dice)
    probs *= hit_probability
    probs[0] += 1 - probs.sum()
    return probs


def expected_damage(distribution):
    return (distribution * np.arange(0, len(distribution))).sum()


def ac_scan(to_hit, damage_dice):
    acs = np.arange(0, 35)
    average = np.zeros(len(acs))
    for i, ac in enumerate(acs):
        prob = attack(to_hit, ac)

        average[i] = expected_damage(damage_distribution(prob, damage_dice))
    return acs, average


def modifier_scan(spell_save_dc, damage_dice, half_on_fail=True):
    mods = np.arange(-4, 6)
    average = np.zeros(len(mods))
    for i, mod in enumerate(mods):
        prob = spell(spell_save_dc, mod)
        average[i] = expected_damage(damage_distribution(prob, damage_dice, half_on_fail))
    return mods, average


a, b = ac_scan(4, "1d8+2")
c, d = modifier_scan(13, "1d8")

d = pd.read_csv("monster stats.csv")