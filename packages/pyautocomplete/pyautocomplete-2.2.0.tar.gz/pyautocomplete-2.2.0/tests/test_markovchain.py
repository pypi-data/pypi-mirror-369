"""
Test pycomplete/markovchain.py
"""

from pycomplete.markovchain import MarkovChain
import pytest


# TEST: initialization
def test_init():
    """
    Tests that adding a string to the Markov chain works.

    This also tests that likeliest() works 
    """

    m = MarkovChain()
    m.add_item("lebron")
    assert m.likeliest() == "lebron"

def test_init_remove():
    """
    Tests we have an empty list
    """

    m = MarkovChain()
    assert not m.contains("")

# TEST: add_item
def test_add_item_works():
    """
    Tests that when we call add_item, the Markov chain
    contains the items 
    """

    m = MarkovChain()
    m.add_item("lebron")
    assert m.contains("lebron")

def test_likeliest_returns_most_frequent_with_adds():
    """
    Tests that the likeliest() funciton returns the most
    frequently used word based on add_item only.
    """

    m = MarkovChain()
    m.add_item("lebron")
    m.add_item("james")
    m.add_item("who")
    m.add_item("who")
    m.add_item("james")
    m.add_item("james")
    assert m.likeliest() == "james"


# TEST: remove_item
def test_remove_item_single():
    """
    Test adding and remove an item ensures that the item doesn't exist 
    """

    m = MarkovChain()
    m.add_item("lebron")
    m.remove_item("lebron")
    assert not m.contains("lebron")

def test_remove_item_likeliest():
    """
    Test that removing the likeliest item makes updates the new likeliest item.
    """

    m = MarkovChain()
    m.add_item("leroy")
    m.add_item("leroy")
    m.add_item("who")
    m.add_item("who")
    m.remove_item("leroy")
    assert m.likeliest() == "who"

def test_remote_item_nonexistent():
    """
    Test that removing and item that doesn't exist throws an error
    """
    with pytest.raises(KeyError):
        m = MarkovChain()
        m.remove_item("LEBRON JAMES")
    
