import numpy as np


def roll_character(modifier, advantage, N):
    if advantage:
        rolls = np.random.randint(1, 20, size=(N, 2)).max(axis=1) + modifier
    else:
        rolls = np.random.randint(1, 20, size=N) + modifier
    return rolls


def camp_quality(characters, DC, N):
    rolls = np.zeros((N, len(characters)))
    for i, c in enumerate(characters):
        rolls[:, i] = roll_character(*c, N)
    success_count = (rolls >= DC).sum(axis=1)
    quality = np.zeros(N)
    quality[np.where(success_count == len(characters))] = 2
    quality[np.where(success_count < len(characters)/2)] = -2
    return quality


def camping_outcome(characters, DC, other_modifiers, N):
    camp_modifier = camp_quality(characters, DC, N)
    results = camp_modifier + other_modifiers
    output = np.zeros(4)
    output[0] = (results <= -5).sum()
    output[1] = (np.logical_and(results > -5, results < 0)).sum()
    output[2] = (np.logical_and(results >= 0, results < 5)).sum()
    output[3] = (results >= 5).sum()
    return output/N


z = camp_quality([(3, False), (4, True)], 15, 100)

level_three_party = [(3, False), (4, True)]
level_nine_party = [(5, False), (7, True)]
level_three_full_party = [(3, False), (4, True), (3, True), (1, False)]
level_three_all = [(3, False), (4, True), (3, True)]


N = 1000

# Inn in Town
DC = 0
other_modifiers = 3 + 1 + 1
print('\nIn Town')
print(f'Level 3: {camping_outcome(level_three_party, DC, other_modifiers, N)}')
print(f'Level 9: {camping_outcome(level_nine_party, DC, other_modifiers, N)}')

# Mild wilderness
DC = 10
other_modifiers = -3 + -1 + 1 + 1 + 1 + -1
print('\nMild Wilderness')
print(f'Level 3: {camping_outcome(level_three_party, DC, other_modifiers, N)}')
print(f'Level 9: {camping_outcome(level_nine_party, DC, other_modifiers, N)}')

# An untamed wilderness
DC = 15
other_modifiers = -3 + -1 + 1 + 1 + -1
print('\nUntamed Wilderness')
print(f'Level 3: {camping_outcome(level_three_party, DC, other_modifiers, N)}')
print(f'Level 3 - all: {camping_outcome(level_three_full_party, DC, other_modifiers, N)}')
print(f'Level 3 - 3 people: {camping_outcome(level_three_party, DC, other_modifiers, N)}')
print(f'Level 9: {camping_outcome(level_nine_party, DC, other_modifiers, N)}')

# An untamed wilderness after a bad day
DC = 15
other_modifiers = -3 + -1 + 1 + -1 + -1
print('\nUntamed Wilderness after a bad day')
print(f'Level 3: {camping_outcome(level_three_party, DC, other_modifiers, N)}')
print(f'Level 9: {camping_outcome(level_nine_party, DC, other_modifiers, N)}')