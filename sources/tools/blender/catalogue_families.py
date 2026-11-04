"""Reference-driven assembly families; each catalogue entry supplies its own reviewed parameters."""
import math
from catalogue_recipe_parts import (Recipe, block_complex, crystal_complex, organic_complex,
                                    ring_habitat, saucer, storage)


def make_recipe(family, p):
    r = Recipe()
    n = p.get('n', 3)
    h = p.get('h', 2.4)
    if family == 'habitat':
        ring_habitat(r, p.get('floors', 2), p.get('radius', 0.9), p.get('protected', False))
    elif family == 'storage':
        storage(r, p.get('tiers', 1), p.get('protected', False))
    elif family == 'mushrooms':
        for i in range(n):
            a = i * math.tau / n
            x, y = 0.83 * math.cos(a), 0.83 * math.sin(a)
            r.lathe('Mushroom support', [x, y, 0], [[0, 0.42], [0.13, 0.39], [0.67, 0.21]], 'body')
            r.dome('Mushroom collector cap', [x, y, 0.65], 0.51, 0.28, 'glass')
    elif family == 'pipe_cluster':
        for i in range(n):
            x, y = (i - (n - 1) / 2) * 0.55, 0.3 * (i % 2)
            z = h - (i % 2) * 0.40
            r.cylinder('Vertical filtration pipe', [x, y, z / 2], 0.20, z, 'body')
            r.rod('Angled filtration intake', [x, y, z], [x, y - 0.45, z + 0.17], 0.22, 'body')
            r.rod('Dark intake opening', [x, y - 0.46, z + 0.17], [x, y - 0.49, z + 0.18], 0.16, 'dark')
    elif family == 'fan':
        r.tower(0, 0, 0.45, 1.0, 'spire', mat='cap')
        for i in range(n):
            a = -0.9 + i * 1.8 / max(1, n - 1)
            r.box('Upright collector blade', [math.sin(a) * 0.55, 0, 1.75], [0.24, 0.08, 1.7],
                  'glass', [0, a, 0])
    elif family == 'factory':
        r.box('Low factory main hall', [0, 0.15, 0.55], [2.6, 1.6, 0.95], 'cap')
        for i in range(3):
            r.box('Factory roof service strip', [(i - 1) * 0.7, 0.15, 1.05], [0.36, 1.60, 0.05], 'glass')
        for i in range(n):
            r.tower((i - (n - 1) / 2) * 0.62, -1.0, 0.27, 0.86, cap=False, mat='purple')
            r.dome('Factory auxiliary tank cap', [(i - (n - 1) / 2) * 0.62, -1.0, 0.86], 0.28, 0.18, 'glass')
        r.windows(0, -0.67, 0.25, 2, 5)
    elif family == 'mine':
        r.box('Raised mine deck', [0, 0, 1.52], [2.15, 1.85, 0.46], 'cap')
        for x in [-0.75, 0.75]:
            for y in [-0.65, 0.65]:
                for dx, dy in [(-0.1, -0.1), (0.1, 0.1)]:
                    r.rod('Mine trestle leg', [x + dx, y + dy, 0], [x + dx, y + dy, 1.4], 0.025)
                for z in [0.15, 0.55, 0.95]:
                    r.rod('Mine trestle cross brace', [x - 0.1, y - 0.1, z], [x + 0.1, y + 0.1, z + 0.34], 0.018)
        r.dome('Mine deck dome', [-0.40, -0.20, 1.76], 0.32, 0.20, 'body')
        r.cylinder('Mine rear hatch', [0.35, 0.39, 1.78], 0.34, 0.05, 'glass')
        r.windows(0, -0.94, 1.49, 1, n)
        if p.get('deep'):
            r.cylinder('Deep drilling shaft', [0, 0, 0.70], 0.36, 1.40, 'trim')
    elif family == 'silo':
        r.lathe('Silo flared bunker', [0, 0, 0], [[0, 1.08], [0.2, 1.17], [0.65, 0.91]], 'cap')
        r.dome('Silo armoured lid', [0, 0, 0.63], 0.89, 0.22, 'accent')
        r.ring('Silo lid seam', [0, 0, 0.67], 0.91, 0.025, 'dark')
        if p.get('annex'):
            r.tower(0, -1.03, 0.25, 0.35, 'bulb')
        else:
            r.windows(0, -1.10, 0.30, 1, 4)
    elif family == 'shield':
        r.floor(1.0, height=0.3)
        r.dome('Shield generator low housing', [0, 0, 0.28], 0.98, 0.38, 'body')
        for i in range(n):
            x = (i - (n - 1) / 2) * 0.65
            r.rod('Shield emitter stem', [x, 0, 0.5], [x, 0, h], 0.04)
            for side in [-1, 1]:
                r.rod('Shield emitter cage', [x, 0, 0.9], [x + side * 0.16, 0, h - 0.3], 0.025, 'light')
                r.rod('Shield cage crown', [x + side * 0.16, 0, h - 0.3], [x, 0, h], 0.025, 'light')
    elif family == 'teleporter':
        r.floor(0.9, 'cap', 0.4)
        r.tower(0, 0.15, 0.36, 1.9, cap=True, mat='body')
        r.dish(0, 0.15, 2.1, 0.35)
        r.tower(-0.65, -0.2, 0.17, 0.8)
        r.tower(0.65, -0.2, 0.17, 0.8)
        r.sphere('Transfer energy core', [0, -0.6, 0.60], [0.35, 0.24, 0.26], 'light')
        r.box('Transfer ramp', [0, -1.0, 0.2], [0.35, 0.8, 0.08], 'cap', [0.3, 0, 0])
    elif family == 'orb_drive':
        r.floor(1.25, height=0.25)
        r.sphere('Central segmented field orb', [0, 0, 1.35], [0.82, 0.82, 0.91], 'purple')
        r.ring('Field orb equator seam', [0, 0, 1.35], 0.82, 0.024, 'dark')
        if p.get('satellites'):
            for i in range(3):
                a = i * math.tau / 3
                r.sphere('Peripheral field orb', [0.81 * math.cos(a), 0.81 * math.sin(a), 0.5], [0.43, 0.43, 0.46], 'purple')
        else:
            r.rod('Orb axial dividing seam', [0, -0.815, 0.9], [0, -0.815, 1.95], 0.018, 'dark')
        r.windows(0, -0.83, 1.1, 2, 1, mat='red')
    elif family == 'workshop':
        r.tower(0, 0, 0.82, h, cap=False, mat='purple')
        r.dome('Workshop gold roof', [0, 0, h], 0.7, 0.26)
        for i in range(6):
            a = i * math.tau / 6
            r.rod('Workshop exterior rib', [0.85 * math.cos(a), 0.85 * math.sin(a), 0.2],
                  [0.85 * math.cos(a), 0.85 * math.sin(a), h - 0.1], 0.06, 'trim')
        r.windows(0, -0.84, 0.3, 7, 2, 0.22)
    elif family == 'sensor':
        r.tower(0, 0, 0.23, h, 'spire', mat='body')
        for i in range(8):
            r.ring('Sensor mast collar', [0, 0, i * h / 9 + 0.1], 0.18, 0.025)
        r.dome('Sensor pickup cap', [0, 0, h], 0.19, 0.18, 'glass')
        r.aerial(0, 0, h + 0.18, 0.5)
    elif family == 'turret':
        r.lathe('Turret armoured pedestal', [0, 0, 0], [[0, 0.92], [0.2, 0.98], [0.9, 0.50]], p.get('pedestal', 'accent'))
        r.gun(p.get('barrels', 1), z=1.03, length=p.get('length', 1.0), radius=p.get('bore', 0.10), mat='cap')
        if p.get('dish'):
            r.sphere('Turret sloped reflector', [0, -0.1, 1.35], [0.70, 0.32, 0.50], 'cap')
        r.windows(0.40, -0.57, 0.36, 1, 1, mat='red')
    elif family == 'wedge':
        r.floor(0.95, 'purple', 0.32)
        r.add('wedge', 'Sloping industrial housing', position=[0, 0, 0.30], size=[2.1, 2.0, h * 0.55], material='cap')
        for x in [-0.3, 0.3]:
            r.dome('Housing top service hatch', [x, 0.30, h * 0.56], 0.16, 0.08, 'trim')
        r.windows(0, -1.01, 0.5, 1, 3)
        if p.get('mast'):
            r.aerial(-0.7, 0.6, 0.8, 1.3)
    elif family == 'reactor':
        r.lathe('Reactor flared base', [0, 0, 0], [[0, 1.12], [0.15, 1.2], [0.45, 0.72]], 'trim')
        r.cylinder('Reactor raised deck', [0, 0, 0.75], 0.92, 0.30, 'trim')
        r.tower(0, 0, 0.30, 1.4, 'bulb', mat='cap')
        for i in range(n):
            a = i * math.tau / n
            r.sphere('Reactor cooling vessel', [0.68 * math.cos(a), 0.68 * math.sin(a), 1.23], [0.26, 0.26, 0.40], 'glass')
            r.rod('Reactor radial conduit', [0.6 * math.cos(a), 0.6 * math.sin(a), 0.45],
                  [1.25 * math.cos(a), 1.25 * math.sin(a), 0.15], 0.09, 'cap')
    elif family == 'command':
        r.tower(0, 0, 0.76, h, cap=True)
        for i in range(n):
            a = i * math.tau / n
            x, y = 0.95 * math.cos(a), 0.95 * math.sin(a)
            r.box('Command vertical fin', [x, y, h * 0.5], [0.32, 0.35, h], 'cap', [0, 0, a])
        r.windows(0, -0.77, 0.4, 5, 2)
    elif family == 'yard':
        r.floor(1.35, 'cap', 0.20)
        r.ring('Shipyard perimeter wall', [0, 0, 0.4], 1.22, 0.13)
        for i in range(n):
            a = i * math.tau / n
            r.cylinder('Shipyard machinery pad', [0.80 * math.cos(a), 0.80 * math.sin(a), 0.30], 0.25, 0.20, 'body')
        for x in [-0.6, 0.6]:
            r.rod('Shipyard gantry upright', [x, 0, 0.3], [x, 0, 1.40], 0.045)
        r.rod('Shipyard crane beam', [-0.95, 0, 1.42], [0.95, 0, 1.42], 0.075)
        r.box('Crane trolley', [0.2, 0, 1.3], [0.23, 0.25, 0.2], 'accent')
    elif family == 'pad':
        r.floor(1.12, 'cap', 0.15, True)
        r.box('Landing pad inset', [0, 0, 0.18], [1.77, 1.77, 0.04], 'trim')
        for x in [-0.38, 0, 0.38]:
            r.box('Landing pad runway stripe', [x, 0, 0.21], [0.16, 1.35, 0.025], 'red')
    elif family == 'matrix':
        r.floor(0.43, 'purple', 0.5)
        for x in [-0.20, 0.20]:
            r.cylinder('Solar matrix pillar', [x, 0, 1.5], 0.12, 2.0, 'body')
            for index in range(18):
                r.ring('Solar matrix coil', [x, 0, 0.55 + index * 0.106], 0.13, 0.025, 'glass')
        r.dome('Solar matrix crown', [0, 0, 2.5], 0.35, 0.35, 'body')
        r.panels(4, 2.85, 0.75)
        if p.get('protected'):
            r.aerial(0, 0, 2.85, 0.55)
    elif family == 'fuel':
        r.tower(0, 0, 0.46, h, cap=False, mat='bronze')
        for index in range(n):
            z = 0.45 + index * 0.80
            r.cylinder('Fuel reservoir band', [0, 0, z], 0.49, 0.40, 'body')
            r.ring('Fuel band upper rim', [0, 0, z + 0.2], 0.5, 0.035)
        r.tower(0.5, -0.2, 0.27, h * 0.52, 'bulb', mat='bronze')
    elif family == 'medical':
        r.floor(1.15, height=0.4)
        r.dome('Medical care dome', [0, 0, 0.4], 0.95, 0.6, 'glass')
        r.box('Medical roof marker vertical', [0, -0.3, 0.99], [0.15, 0.6, 0.04], 'red')
        r.box('Medical roof marker horizontal', [0, -0.3, 1.0], [0.6, 0.15, 0.04], 'red')
        for x in [-0.4, 0.4]:
            r.tower(x, -1.0, 0.23, 0.62, 'cylinder', mat='bronze')
    elif family == 'disc_stack':
        r.floor(0.6, 'cap', 0.35)
        for index in range(n):
            z = 0.5 + index * 0.60
            r.lathe('Environmental circulation disk', [0, 0, z], [[0, 0.6], [0.10, 0.91], [0.26, 0.93], [0.45, 0.54]], 'purple')
            r.cylinder('Disk connecting neck', [0, 0, z + 0.46], 0.31, 0.3, 'dark')
        r.aerial(0, 0, 0.5 + n * 0.60, 0.18)
    elif family == 'pleasure':
        r.floor(1.2, height=0.2)
        r.dome('Pleasure glazed canopy', [0, 0, 0.2], 1.15, 0.85, 'glass')
        r.add('wedge', 'Pleasure dome front entrance', position=[0, -0.95, 0.15], size=[1.05, 0.8, 0.65], material='cap')
        for x in [-0.75, 0.75]:
            r.box('Pleasure dome entrance wing', [x, -0.83, 0.3], [0.5, 0.38, 0.2], 'accent')
        r.aerial(-0.6, -0.6, 0.8, 0.6)
    elif family == 'spindle':
        r.tower(0, 0, p.get('r', 0.75), h, 'hourglass', cap=False)
        for index in range(n):
            z = h * (0.5 + index * 0.15)
            r.lathe('Spindle saucer platform', [0, 0, z], [[0, 0.35], [0.10, 0.82], [0.26, 0.75]], 'body')
            r.windows(0, -0.76, z + 0.09, 1, 3)
        if p.get('aerial', True):
            r.aerial(0, 0, h + 0.1, p.get('mast', 0.7), p.get('fork', False), 'cap')
    elif family == 'tier_tower':
        r.tower(0, 0, p.get('r', 0.65), h, p.get('style', 'cylinder'), cap=p.get('cap', True))
        for index in range(p.get('tiers', 0)):
            z = 0.5 + index * 0.55
            r.ring('Tower intermediate ledge', [0, 0, z], p.get('r', 0.65) * 1.1, 0.09)
        if p.get('mast'):
            r.aerial(0, 0, h + 0.2, p['mast'], p.get('fork', True), 'cap')
    elif family == 'spire_cluster':
        r.cluster(n, p.get('r', 0.38), h, p.get('spread', 0.7), 'spire', p.get('centre'))
        for i in range(n):
            a = i * math.tau / n + math.pi / 2
            r.aerial(p.get('spread', 0.7) * math.cos(a), p.get('spread', 0.7) * math.sin(a), h, 0.4)
    elif family == 'crystals':
        crystal_complex(r, n, h, p.get('halo', False), p.get('mast', False), p.get('arms', 0))
        if p.get('mark'):
            for z in [0.3, 0.55, 0.8]:
                r.box('Crystal red identifying inset', [0.6, -0.55, z], [0.20, 0.04, 0.08], 'red')
    elif family == 'organic':
        organic_complex(r, p.get('towers', 1), h, p.get('satellites', 0), p.get('mast', False), p.get('stacked', 0))
        if p.get('gun'):
            r.gun(p.get('barrels', 1), h, p.get('length', 1.0), 0.12)
    elif family == 'block':
        block_complex(r, p.get('levels', 2), p.get('wings', 0), p.get('mast', 0), p.get('openings', False))
        if p.get('gun'):
            r.gun(p.get('barrels', 1), p.get('levels', 2) * 0.82 + 0.5, 1.1, 0.14)
    elif family == 'saucer':
        saucer(r, p.get('tiers', 1), p.get('radius', 1.2), p.get('mast', 0), p.get('rim', False))
        if p.get('pods'):
            for i in range(p['pods']):
                a = i * math.tau / p['pods']
                r.dome('Saucer roof auxiliary pod', [0.5 * math.cos(a), 0.5 * math.sin(a), 0.4 * p.get('tiers', 1)], 0.28, 0.30)
        if p.get('gun'):
            r.gun(p.get('barrels', 1), p.get('tiers', 1) * 0.42 + 0.25, p.get('length', 0.9), 0.13)
    elif family == 'ring_yard':
        for x in [-0.65, 0.65]:
            r.ring('Open construction bay ring', [x, 0, 0.35], 0.66, 0.14)
            r.cylinder('Construction bay dark well', [x, 0, 0.15], 0.55, 0.15, 'dark')
            for y in [-0.35, 0.35]:
                r.rod('Construction bay support', [x, y, 0.2], [x, y, 1.1], 0.045)
        r.cylinder('Raised central construction console', [0, 0.4, 1.0], 0.5, 0.25, 'body')
        if p.get('armament'):
            r.aerial(-0.85, 0.4, 0.45, 2.1, True, 'cap')
            r.box('Arms fabrication machinery', [0.65, 0.10, 0.75], [0.45, 0.35, 0.60], 'accent')
    elif family == 'triple_tanks':
        r.cluster(n, p.get('r', 0.4), h, p.get('spread', 0.65), p.get('style', 'cylinder'))
        for index in range(n):
            a = index * math.tau / n + math.pi / 2
            x, y = p.get('spread', 0.65) * math.cos(a), p.get('spread', 0.65) * math.sin(a)
            r.rod('Tank service conduit', [x, y - 0.2, 0.1], [x, y - 0.2, h + 0.1], 0.04, 'trim')
    elif family == 'sphere_power':
        r.floor(0.65, height=0.25)
        r.tower(0, 0, 0.25, 0.6, cap=False)
        r.sphere('Power globe', [0, 0, 1.3], [0.85, 0.85, 0.9], 'trim')
        r.sphere('Power globe central lens', [0, -0.79, 1.3], [0.28, 0.10, 0.28], 'glass')
        r.ring('Globe equator seam', [0, 0, 1.3], 0.84, 0.035, 'body')
    elif family == 'rotor':
        r.tower(0, 0, 0.6, 1.0, cap=True)
        r.rod('Rotor inclined support', [0, 0, 1.1], [0, 0.2, 2.2], 0.08)
        r.panels(n, 2.2, 0.85)
        r.cylinder('Rotor pivot', [0, 0, 2.25], 0.15, 0.2, 'cap')
    else:
        raise ValueError('No authored assembly for ' + family)
    return r.parts
