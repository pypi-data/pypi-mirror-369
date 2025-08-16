import pytest
from BDviz.plotbd import BrownDwarf, Plot3D

@pytest.fixture
def bd():
    return BrownDwarf("BD-Test", ra=150, dec=20, distance=5, color='purple')

@pytest.fixture
def plot():
    # Patch plt.show so it doesn't pop up during tests
    #suggestion and function from ChatGPT
    import matplotlib.pyplot as plt
    plt.show = lambda: None
    return Plot3D()

def test_plot3d_initialization(plot):
    assert plot.ax.get_xlim() == (-1, 1)
    assert plot.ax.get_xlabel() == "X (pc)"
    assert isinstance(plot.objects, list)
    assert isinstance(plot.artists, dict)

def test_add_object_adds_browndwarf(plot, bd):
    plot.add_object(bd)

    assert bd in plot.objects
    assert bd.name in plot.artists
    assert len(plot.artists[bd.name]) >= 1  
    assert hasattr(bd, "x") and hasattr(bd, "y") and hasattr(bd, "z")

def test_remove_object(plot, bd):
    plot.add_object(bd)
    plot.remove_object(bd.name)

    assert bd not in plot.objects
    assert bd.name not in plot.artists
