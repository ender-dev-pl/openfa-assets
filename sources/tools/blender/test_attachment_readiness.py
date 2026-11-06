"""Controlled checks for attachment-frame math and declaration/export comparisons."""
import math
import sys
from pathlib import Path

from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_attachment_readiness import axis_vector, root_frame, declared_socket_checks, compare


def near(actual, expected):
    assert max(abs(a-b) for a, b in zip(actual, expected)) < 1e-6


def main():
    for axis, expected in [('local +Z', (0, 0, 1)), ('local -Y', (0, -1, 0)), ('local -X', (-1, 0, 0))]:
        near(axis_vector(axis), expected)
    root = Matrix.Translation((8, 3, -2)) @ Matrix.Rotation(.7, 4, 'Z')
    local = Matrix.Translation((2, -1, .4)) @ Matrix.Rotation(math.pi/2, 4, 'X')
    frame = root_frame(root @ local, root, 'local +Z')
    near(frame['position'], (2, -1, .4))
    near(frame['forward'], (0, -1, 0))
    helper = dict(parent='PlacementRoot', properties={'forward_axis': 'local +Z'}, root_frame=frame)
    state = dict(helpers={'Test socket': helper})
    declarations = dict(sockets={'Test socket': dict(position=[2, -1, .4], forward=[0, -3, 0], status='authored-uncalibrated')})
    checks = declared_socket_checks(declarations, state)
    assert checks[0]['position_error'] < 1e-6 and checks[0]['forward_error'] < 1e-6
    assert not declared_socket_checks(declarations, dict(helpers={}))[0]['present']
    assert compare(state, state)['common']['Test socket']['matrix_error'] == 0
    assert compare(state, dict(helpers={}))['missing'] == ['Test socket']
    altered = dict(helpers={'Test socket': dict(helper, properties={})})
    assert compare(state, altered)['common']['Test socket']['properties_equal'] is False
    for invalid in ['world +Z', 'local Q']:
        try:
            axis_vector(invalid)
        except AssertionError:
            pass
        else:
            raise AssertionError('Unknown axis must not be guessed')
    try:
        root_frame(Matrix.Identity(4), Matrix.Diagonal((1, 0, 1, 1)), 'local +Z')
    except AssertionError:
        pass
    else:
        raise AssertionError('Singular placement frame must be rejected')
    print('ATTACHMENT_READINESS_TEST_OK', flush=True)


if __name__ == '__main__':
    main()
