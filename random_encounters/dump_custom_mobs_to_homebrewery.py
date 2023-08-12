from mob_sets import FULL_MONSTERS

sections = {
    "Horrible Bugs": ['giant millipede', 'adult giant millipede'],
    "Ankhegs": ['ankheg tunneler', 'ankheg worker', 'ankheg queen'],
    'Ogres': ['boulder thrower'],
    'Harpies': ['wingmistress', 'harpy matriarch'],
    'Satyrs': ['satyr marksman', 'satyr charger']
}

n = 0
for section_name, monsters in sections.items():
    print(f'### {section_name}')
    for monster in monsters:
        if n%3 == 0 and n > 0:
            print('\page\n')
        print(FULL_MONSTERS[monster].to_homebrewery())
        n += 1
