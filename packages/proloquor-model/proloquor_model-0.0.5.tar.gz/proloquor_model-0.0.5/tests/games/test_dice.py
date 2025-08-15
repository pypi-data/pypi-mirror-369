import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

from proloquor_model.games.dice import Dice

def test_dice():
    d = Dice(8)
    
    assert (len(d) == 8)
    assert (str(d) == "1, 1, 1, 1, 1, 1, 1, 1")
    assert (d.total() == 8)

def test_roll():
    d = Dice().roll()

    assert (d.total() != 5)