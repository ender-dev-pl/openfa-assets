"""Pure-data solid modelling vocabulary for individually authored catalogue recipes."""
import math


class Recipe:
    def __init__(self):
        self.parts = []

    def add(self, kind, name, **values):
        self.parts.append(dict(kind=kind, name=name, **values))

    def box(self, name, p, size, mat='body', rotation=None):
        self.add('box', name, position=p, size=size, material=mat, rotation=rotation or [0, 0, 0])

    def lathe(self, name, p, profile, mat='body', segments=32):
        self.add('lathe', name, position=p, profile=profile, material=mat, segments=segments)

    def cylinder(self, name, p, radius, height, mat='body', segments=24):
        self.lathe(name, p, [[-height / 2, radius], [height / 2, radius]], mat, segments)

    def dome(self, name, p, radius, height, mat='cap'):
        self.add('dome', name, position=p, radius=radius, height=height, material=mat)

    def sphere(self, name, p, size, mat='body', faceted=False):
        self.add('sphere', name, position=p, size=size, material=mat, faceted=faceted)

    def rod(self, name, a, b, radius=0.035, mat='trim'):
        self.add('rod', name, start=a, end=b, radius=radius, material=mat)

    def ring(self, name, p, radius, tube=0.035, mat='trim'):
        self.add('ring', name, position=p, radius=radius, tube=tube, material=mat)

    def windows(self, x, y, bottom, rows=3, columns=2, spacing=0.20, mat='light'):
        for row in range(rows):
            for column in range(columns):
                self.box('Inset service window', [x + (column - (columns - 1) / 2) * spacing, y,
                         bottom + row * spacing], [0.09, 0.035, 0.11], mat)

    def aerial(self, x, y, z, height=0.6, fork=False, mat='trim'):
        self.rod('Aerial stem', [x, y, z], [x, y, z + height], 0.022, mat)
        if fork:
            for sign in [-1, 1]:
                self.rod('Aerial fork', [x, y, z + height * 0.50], [x + sign * 0.15, y, z + height * 0.76], 0.022, mat)
                self.rod('Aerial fork tine', [x + sign * 0.15, y, z + height * 0.76],
                         [x + sign * 0.15, y, z + height * 1.06], 0.022, mat)

    def tower(self, x, y, radius=0.5, height=2.0, style='cylinder', cap=True, base=0, mat='body'):
        if style == 'block':
            self.box('Rectangular tower', [x, y, base + height / 2], [radius * 2, radius * 2, height], mat)
            self.box('Tower roof cornice', [x, y, base + height], [radius * 2.12, radius * 2.12, 0.12], 'trim')
        elif style == 'spire':
            self.lathe('Tapered spire', [x, y, base], [[0, radius], [height * 0.18, radius], [height, 0.07]], mat, 8)
            self.ring('Spire collar', [x, y, base + height * 0.69], radius * 0.35, 0.06, 'accent')
        elif style == 'bulb':
            self.lathe('Bulb shaped chamber', [x, y, base], [[0, radius * 0.8], [height * 0.22, radius],
                [height * 0.62, radius * 1.12], [height * 0.88, radius * 0.72], [height, radius * 0.25]], mat)
        elif style == 'hourglass':
            self.lathe('Flared spindle column', [x, y, base], [[0, radius], [0.15 * height, radius * 0.92],
                [0.44 * height, radius * 0.35], [0.7 * height, radius * 0.50], [height, radius * 0.82]], mat)
        elif style == 'crystal':
            self.lathe('Faceted crystal tower', [x, y, base], [[0, radius * 0.75], [height * 0.22, radius],
                [height * 0.7, radius * 0.8], [height, 0.025]], mat, 5)
        else:
            self.cylinder('Cylindrical tower', [x, y, base + height / 2], radius, height, mat)
            self.ring('Tower seam', [x, y, base + height * 0.64], radius, 0.025)
        if cap and style not in ['spire', 'crystal', 'block']:
            cap_radius = radius * (0.32 if style == 'bulb' else 0.96)
            self.dome('Tower crown', [x, y, base + height], cap_radius, cap_radius * 0.45, 'cap')
        if style != 'crystal':
            if style == 'hourglass':
                profile = [(0,1),(0.15,0.92),(0.44,0.35),(0.7,0.50),(1,0.82)]
            elif style == 'bulb':
                profile = [(0,0.8),(0.22,1),(0.62,1.12),(0.88,0.72),(1,0.25)]
            elif style == 'spire':
                profile = [(0,1),(0.18,1),(1,0.07/radius)]
            else:
                profile = [(0,1),(1,1)]
            for row in range(3):
                relative_z = min(0.90, 0.27 + row * 0.20 / height)
                a,b = next((a,b) for a,b in zip(profile,profile[1:]) if a[0] <= relative_z <= b[0])
                width = radius * (a[1] + (b[1]-a[1]) * (relative_z-a[0])/(b[0]-a[0]))
                self.windows(x, y - width - 0.005, base + height * relative_z, 1, 2)

    def floor(self, radius=1.2, mat='body', height=0.22, square=False):
        if square:
            self.box('Foundation slab', [0, 0, height / 2], [radius * 2, radius * 2, height], mat)
        else:
            self.cylinder('Foundation drum', [0, 0, height / 2], radius, height, mat)

    def cluster(self, count=3, radius=0.45, height=1.7, spread=0.9, style='cylinder', centre_height=None):
        for index in range(count):
            angle = index * math.tau / count + math.pi / 2
            self.tower(spread * math.cos(angle), spread * math.sin(angle), radius, height, style)
        if centre_height:
            self.tower(0, 0, radius * 1.12, centre_height, style)

    def dish(self, x=0, y=0, z=1.0, radius=0.75, mat='trim'):
        self.lathe('Open collector bowl', [x, y, z], [[0, radius * 0.22], [0.12, radius * 0.6],
            [0.35, radius], [0.4, radius], [0.32, radius * 0.86], [0.14, radius * 0.45]], mat)
        self.rod('Collector central pickup', [x, y, z + 0.05], [x, y, z + 0.52], 0.025, 'accent')

    def gun(self, count=1, z=1.3, length=1.0, radius=0.11, mat='accent'):
        self.sphere('Weapon pivot', [0, 0, z], [0.45, 0.43, 0.35], 'body')
        for index in range(count):
            x = (index - (count - 1) / 2) * radius * 3.2
            self.rod('Weapon barrel', [x, -0.15, z + 0.05], [x, -length, z + 0.35], radius, mat)
            self.rod('Weapon dark bore', [x, -length - 0.025, z + 0.355],
                     [x, -length - 0.04, z + 0.36], radius * 0.68, 'dark')

    def panels(self, count=4, z=2.5, size=0.9):
        for index in range(count):
            angle = index * math.tau / count
            self.box('Radial collector panel', [math.cos(angle) * size * 0.78, math.sin(angle) * size * 0.78, z],
                     [size * 1.35, size * 0.72, 0.06], 'glass', [0, 0, angle])


def ring_habitat(r, floors=2, radius=0.9, protected=False):
    r.floor(radius * 0.78, 'body', 0.45)
    for index in range(floors):
        z = 0.5 + index * 0.58
        r.lathe('Stacked residential saucer', [0, 0, z], [[0, radius * 0.83], [0.12, radius],
                [0.36, radius], [0.53, radius * 0.78]], 'cap')
        r.windows(0, -radius - 0.01, z + 0.20, 1, 5)
    r.aerial(0, 0, 0.5 + floors * 0.58, 0.4)
    if protected:
        for index in range(6):
            a = index * math.tau / 6
            r.sphere('Defence side pod', [radius * math.cos(a), radius * math.sin(a), 0.8], [0.20, 0.20, 0.16], 'accent')


def storage(r, tiers=1, protected=False):
    for level in range(tiers):
        base = level * 1.0
        r.cylinder('Storage belt', [0, 0, base + 0.18], 0.78, 0.36, 'body')
        for i in range(4):
            a = i * math.tau / 4
            r.sphere('Exposed storage bulb', [0.47 * math.cos(a), 0.47 * math.sin(a), base + 0.60], [0.34, 0.34, 0.40], 'glass')
    r.lathe('Storage upper hood', [0, 0, tiers - 0.02], [[0, 0.78], [0.18, 0.8], [0.85, 0.54]], 'cap')
    r.dome('Storage hood cap', [0, 0, tiers + 0.83], 0.54, 0.21, 'accent')
    if protected:
        r.aerial(0, 0, tiers + 1.04, 0.6, True)


def block_complex(r, levels=2, wings=0, mast=0.0, openings=False):
    r.floor(1.02, 'body', 0.2, True)
    for level in range(levels):
        size = 1.55 - level * 0.17
        z = 0.25 + level * 0.82
        r.box('Modular block storey', [0, 0, z + 0.38], [size, size, 0.75], 'body')
        r.box('Block roof ledge', [0, 0, z + 0.78], [size + 0.10, size + 0.10, 0.10], 'trim')
        r.windows(0, -size / 2 - 0.02, z + 0.24, 2, 4)
        r.box('Vertical block colour strip', [-size * 0.30, -size / 2 - 0.03, z + 0.38], [0.11, 0.035, 0.7], 'accent')
    for index in range(wings):
        angle = index * math.tau / wings
        x, y = 1.05 * math.cos(angle), 1.05 * math.sin(angle)
        r.box('Block buttress', [x, y, 0.65], [0.36, 0.36, 1.25], 'trim')
        r.cylinder('Buttress metal footing', [x, y, 0.12], 0.12, 0.24, 'cap', 8)
    if mast:
        r.aerial(0.15, 0.18, 0.25 + levels * 0.82, mast, True)
    if openings:
        for x in [-0.4, 0.4]:
            for y in [-0.4, 0.4]:
                r.box('Roof recessed opening', [x, y, 0.3 + levels * 0.82], [0.4, 0.4, 0.025], 'red')


def crystal_complex(r, count=3, height=2.6, halo=False, long_mast=False, arms=0):
    r.floor(1.0, 'body', 0.15)
    r.tower(0, 0, 0.59, height, 'crystal')
    for index in range(count):
        angle = index * math.tau / count
        x, y = 0.70 * math.cos(angle), 0.70 * math.sin(angle)
        r.tower(x, y, 0.34, height * (0.42 + (index % 2) * 0.19), 'crystal')
        r.sphere('Crystal luminous node', [x, y - 0.20, height * 0.23], [0.10, 0.09, 0.10], 'light', True)
    r.sphere('Central luminous node', [0, -0.49, height * 0.55], [0.13, 0.09, 0.13], 'light', True)
    if halo:
        r.ring('Crystal conductive halo', [0, 0, height * 0.49], 0.88, 0.055, 'cap')
    if long_mast:
        r.aerial(0.0, 0.0, height, 0.9, True, 'cap')
    for index in range(arms):
        angle = index * math.tau / arms
        r.rod('Crystal radial strut', [0, 0, 1.3], [1.15 * math.cos(angle), 1.15 * math.sin(angle), 0.35], 0.12, 'trim')


def organic_complex(r, towers=1, height=2.5, satellites=0, mast=False, stacked=0):
    r.floor(1.02, 'body', 0.2)
    if towers == 1:
        r.tower(0, 0, 0.62, height, 'bulb')
    else:
        r.cluster(towers, 0.40, height, 0.65, 'bulb')
    for index in range(satellites):
        angle = index * math.tau / satellites
        x, y = 0.92 * math.cos(angle), 0.92 * math.sin(angle)
        r.tower(x, y, 0.31, 0.7 + 0.20 * (index % 2), 'bulb')
    for index in range(stacked):
        z = height + index * 0.75
        r.sphere('Stacked rounded vessel', [0, 0, z], [0.48, 0.48, 0.49], 'body')
        r.ring('Rounded vessel collar', [0, 0, z - 0.22], 0.39, 0.045, 'cap')
    if mast:
        top = height + (stacked - 1) * 0.75 + 0.48 if stacked else height + 0.08
        r.aerial(0, 0.65 if towers > 1 and not stacked else 0, top, 0.7, True)


def saucer(r, tiers=1, radius=1.2, mast=0.0, rim=False):
    for index in range(tiers):
        z = index * 0.42
        rr = radius * (1 - index * 0.1)
        r.lathe('Terraced oval hull', [0, 0, z], [[0, rr * 0.7], [0.10, rr], [0.26, rr], [0.40, rr * 0.66]], 'body')
    if rim:
        r.ring('Raised open bay rim', [0, 0, 0.42 * tiers], radius * 0.7, 0.12)
        r.cylinder('Dark open bay', [0, 0, 0.40 * tiers], radius * 0.60, 0.05, 'dark')
    if mast:
        r.aerial(-radius * 0.72, 0, tiers * 0.42, mast, True, 'cap')
    r.windows(0, -radius * 0.86, 0.16, 1, 4)
