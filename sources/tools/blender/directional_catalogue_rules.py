"""Source-model heading export coverage, independent of the current runtime allowlist."""


def requires_rig(record):
    return (any(part['name'] == 'Weapon pivot' for part in record['parts'])
            or record['global_type'] in [31, 33, 61, 106])
