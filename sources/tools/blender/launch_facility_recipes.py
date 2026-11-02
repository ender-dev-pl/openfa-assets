"""Culture-specific launch mechanisms. Dimensions/stow engineering are authored hypotheses."""
RECIPES = {
    'PB09': dict(mode='quarters', targets=['Silo armoured lid', 'Silo lid armour leaves'], axis=0, radius=.89, mouth=.62, top=.64),
    'RI18': dict(mode='hinged-cap', targets=['RI18 closed silo cap'], axis=0, radius=.26, mouth=.18, top=1.63),
    'BR11': dict(mode='pyramid', mouth=.65, top=.15, radius=.88, floor=-1.15, terrain_cutout_fraction=.65/2.24),
    'MK11': dict(mode='crown', mouth=.48, top=1.05, radius=.76, trim_above=.98),
    'MK12': dict(mode='energy-spiral', mouth=.36, top=2.65, radius=.56, height=2.55, colour='gold'),
    'MK17': dict(mode='tower-crown', mouth=.36, top=2.25, radius=.56, height=2.15, colour='silver'),
    'AR16': dict(mode='single-lid', mouth=.46, top=1.60, radius=.70, targets=['Cylindrical tower']),
    'MN09': dict(mode='roof', mouth=.58, top=.98, radius=.82),
    'AC12': dict(mode='strip-cover', mouth=.67, top=.46, radius=.76),
    'BR12': dict(mode='open-silo', mouth=.61, top=.64),
    'BR19': dict(mode='open-silo', mouth=.61, top=.64),
    'MN10': dict(mode='open-roof', mouth=.55, top=1.02),
    'MN14': dict(mode='open-roof', mouth=.48, top=1.02),
    'AC13': dict(mode='open-emitter', mouth=.17, top=1.26),
    'AC14': dict(mode='open-emitter', mouth=.17, top=1.16),
}
RETAIN = ['PB26', 'PB14', 'RI10', 'RI11', 'AR09']

CONFIRMED = ['BR11', 'RI18', 'MK12', 'PB09']
