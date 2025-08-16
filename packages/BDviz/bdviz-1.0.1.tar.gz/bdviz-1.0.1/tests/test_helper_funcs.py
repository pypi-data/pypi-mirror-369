from BDviz.helper_functions import get_angular_separation, get_physical_separation
from BDviz.plotbd import BrownDwarf
import astropy.units as u

def test_ang_sep_known():
    bd1 = BrownDwarf("BD-1", ra=150, dec=20, distance=5, color='purple')
    bd2 = BrownDwarf("BD-2", ra=150, dec=25, distance=5, color='purple')

    result = get_angular_separation(bd1, bd2)
    assert result.unit == u.deg

    # Because RA is the same, angular separation = |dec1 - dec2| = 5 deg
    assert abs(result.value - 5.0) < 1e-5

def test_ang_sep_zero():
    bd1 = BrownDwarf("BD-1", ra=150, dec=20, distance=5, color='purple')
    result = get_angular_separation(bd1, bd1)

    assert result.value == 0

def test_phys_sep_known():
    bd1 = BrownDwarf("BD-1", ra=150, dec=20, distance=5, color='blue')  # 5 parsecs
    bd2 = BrownDwarf("BD-2", ra=150, dec=20, distance=10, color='red')  # 10 parsecs

    result = get_physical_separation(bd1, bd2)

    # They are along the same line of sight, so 3D distance is just |10 - 5| = 5 pc
    assert result.unit == u.pc
    assert abs(result.value - 5.0) < 1e-5

def test_phys_sep_zero():
    bd1 = BrownDwarf("BD-1", ra=150, dec=20, distance=5, color='green')
    result = get_physical_separation(bd1, bd1)

    assert result.unit == u.pc
    assert result.value == 0.0

# if __name__ == "__main__":
#     test_ang_sep_known()
#     test_ang_sep_zero()