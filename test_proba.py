import pytest
import proba

def test_summa():
    assert proba.add(14, 88) == sum([14, 88])