import pytest
import proba

def test_sum2():
    assert proba.add(14, 88) == sum([14, 88])