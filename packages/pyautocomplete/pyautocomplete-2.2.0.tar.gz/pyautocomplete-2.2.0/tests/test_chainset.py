"""
Test pycomplete/chainset.py
"""

from pycomplete.chainset import ChainSet
import pytest

# TEST: add
def test_add_exists():
    """
    Tests if adding values makes the key exist
    """
    c = ChainSet()
    c.add("lebron", "james")
    assert c.exists("lebron")

def test_add_multiple():
    """
    Tests that adding multiple Markov chains works
    """

    c = ChainSet()
    c.add("lebron", "james")
    c.add("hi", "hello")
    assert c.exists("lebron") and c.exists("hi")

# TEST: create_chain
def test_create_chain():
    """
    Tests that create_chain gives us something that exists
    """

    c = ChainSet()
    c.create_chain("lebron")
    assert c.exists("lebron")

def test_create_chain_exists_fails():
    """
    Tests that creating a chain that already exists fails 
    """

    with pytest.raises(ValueError):
        c = ChainSet()
        c.create_chain("lebron")
        c.create_chain("lebron")

# TEST: likeliest
def test_add_single_item_gives_likeliest():
    """
    Tests that adding a single item automatically is the likeliest
    """

    c = ChainSet()
    c.add("lebron", "james")
    assert c.likeliest("lebron") == "james"

def test_likeliest_change_adding_multiple_times():
    """
    Tests that the likeliest method actually reflects changes
    when we add multiple items
    """

    c = ChainSet()
    c.add("lebron", "james")
    c.add("lebron", "goat")
    c.add("lebron", "james")
    c.add("lebron", "goat")
    c.add("lebron", "goat")
    assert c.likeliest("lebron") == "goat"

def test_likeliest_fails_when_key_doesnt_exist():
    """
    Tests that the likeliest method fails when the key doesn't exist
    """

    with pytest.raises(ValueError):
        c = ChainSet()
        c.add("lebron", "james")
        c.likeliest("test")
        


# TEST: remove
def test_remove_decreases_likeliest():
    """
    Tests that when we use the remove method, it decreases the chance for likeliest
    """

    c = ChainSet()
    c.add("lebron", "james")
    c.add("lebron", "goat")
    c.add("lebron", "james")
    c.add("lebron", "goat")
    c.add("lebron", "goat")
    c.remove("lebron", "goat")
    c.remove("lebron", "goat")
    assert c.likeliest("lebron") == "james"

def test_remove_fails_when_key_dont_exist():
    """
    Tests that when we use the remove method with a key that doesn't exist,
    we get a ValueError
    """

    with pytest.raises(ValueError):
        c = ChainSet()
        c.add("test", "value")
        c.remove("lebron", "goat")

def test_remove_fails_when_value_dont_exist():
    """
    Tests that when we use the remove function with a value that doesn't exist,
    we get a ValueError
    """

    with pytest.raises(ValueError):
        c = ChainSet()
        c.add("lebron", "james")
        c.remove("lebron", "goat")