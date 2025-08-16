import pytest
import astropy.units as u
from astropy.coordinates import SkyCoord
from BDviz.plotbd import BrownDwarf

def test_browndwarf_init():
    bd = BrownDwarf("BD-1", ra=150, dec=20, distance=5)

    assert bd.name == "BD-1"
    assert bd.ra == 150 * u.deg
    assert bd.dec == 20 * u.deg
    assert bd.distance == 5 * u.pc
    assert isinstance(bd.pos, SkyCoord)
    assert bd.pos.ra == bd.ra
    assert bd.pos.dec == bd.dec
    assert bd.pos.distance == bd.distance

def test_browndwarf_opts():
    bd = BrownDwarf("BD-Temp", ra=150, dec=20, distance=5, color="red", temp=1000)

    assert bd.color == "red"
    assert bd.temp == 1000

def test_get_xyz_sets_attributes():
    bd = BrownDwarf("BD-XYZ", ra=150, dec=20, distance=5)
    
    with pytest.raises(AttributeError):
        _ = bd.x
    
    bd.get_xyz()
    
    assert isinstance(bd.x, float)
    assert isinstance(bd.y, float)
    assert isinstance(bd.z, float)

    r = (bd.x**2 + bd.y**2 + bd.z**2)**0.5
    assert abs(r - 5.0) < 1e-3  # 5 pc

# if __name__ == "__main__":
#     test_get_xyz_sets_attributes()
#     test_browndwarf_opts()
#     test_browndwarf_init()

