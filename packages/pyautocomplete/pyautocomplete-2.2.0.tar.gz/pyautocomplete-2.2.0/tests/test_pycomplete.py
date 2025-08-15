"""
Test pycomplete/pycomplete.py
"""

from pycomplete.pycomplete import PyComplete
import pytest
import os

# TEST: predict
def test_empty_pycomplete():
    """
    Tests that this works even when we pass in an empty string
    """

    p = PyComplete("")
    assert p.predict("lebron") == []


def test_singleton_pycomplete():
    """
    Tests that this works even when we pass in a string with only a single word
    """

    p = PyComplete("lebron")
    assert p.predict("lebron") == []


def test_predict_throws_error_num_less_one():
    """
    Tests that when we pass in num less than 1, 
    """

    with pytest.raises(ValueError):
        p = PyComplete("lebron james")
        p.predict("lebron", num=0)


def test_predict_works_properly_easy():
    """
    Tests that predict works in the normal use case (EASY)
    """

    p = PyComplete("lebron james is the greatest ")
    assert p.predict("l") == ["lebron", "james"]

def test_predict_works_properly_harder():
    """
    Tests that predict works in the normal use case (HARDER)
    """

    p = PyComplete("no one not two note three noted four no one no two no two no two")
    assert p.predict("n") == ["no", "two"]
    assert p.predict("no") == ["no", "two"]
    assert p.predict("not") == ["not", "two"]
    assert p.predict("note") == ["note", "three"]
    assert p.predict("noted") == ["noted", "four"]

# TEST: add_pair
def test_add_pair_influences_decisons():
    """
    Tests that add_pair influences
    """
    p = PyComplete("no one not two note three noted four no one")
    assert p.predict("n") == ["no", "one"]
    assert p.predict("no") == ["no", "one"]
    assert p.predict("not") == ["not", "two"]
    assert p.predict("note") == ["note", "three"]
    assert p.predict("noted") == ["noted", "four"]
    p.add_pair("no", "two")
    p.add_pair("no", "two")
    p.add_pair("no", "two")
    assert p.predict("n") == ["no", "two"]
    assert p.predict("no") == ["no", "two"]

def test_add_pair_nonexistent_value():
    """
    Tests that add_pair works properly for values that don't exist
    """

    p = PyComplete("no one not two note three noted four no one")
    assert p.predict("n") == ["no", "one"]
    assert p.predict("no") == ["no", "one"]
    assert p.predict("not") == ["not", "two"]
    assert p.predict("note") == ["note", "three"]
    assert p.predict("noted") == ["noted", "four"]
    p.add_pair("no", "ten")
    p.add_pair("no", "ten")
    p.add_pair("no", "ten")
    assert p.predict("n") == ["no", "ten"]
    assert p.predict("no") == ["no", "ten"]

def test_add_pair_nonexistent_key():
    """
    Tests that add_pair works properly for keys that don't exist
    """

    p = PyComplete("no one not two note three noted four no one")
    assert p.predict("n") == ["no", "one"]
    assert p.predict("no") == ["no", "one"]
    assert p.predict("not") == ["not", "two"]
    assert p.predict("note") == ["note", "three"]
    assert p.predict("noted") == ["noted", "four"]
    p.add_pair("n", "one")
    p.add_pair("n", "one")
    p.add_pair("n", "one")
    assert p.predict("n") == ["n", "one"]

def test_add_pair_nonexistent_key_value():
    """
    Tests that add_pair works properly for keys and values that don't exist
    """

    p = PyComplete("no one not two note three noted four no one")
    assert p.predict("n") == ["no", "one"]
    assert p.predict("no") == ["no", "one"]
    assert p.predict("not") == ["not", "two"]
    assert p.predict("note") == ["note", "three"]
    assert p.predict("noted") == ["noted", "four"]
    p.add_pair("n", "ten")
    p.add_pair("n", "ten")
    p.add_pair("n", "ten")
    assert p.predict("n") == ["n", "ten"]

# TEST: add_line
def test_add_line_empty_line_does_nothing():
    """
    When we add an empty line, nothing should be changed
    """

    p = PyComplete("lebron james")
    p.add_line("")
    assert p.predict("lebr") == ["lebron", "james"]

def test_add_line_nonempty_works():
    """
    When we add a non-empty line, we should see some reflected changes
    """

    p = PyComplete("lebron james")
    assert p.predict("lebr") == ["lebron", "james"]

    p.add_line("lebron is the goat lebron is the goat")
    assert p.predict("lebr") == ["lebron", "is"]


# TEST: from_text_file
def test_from_text_file_empty():
    """
    Tests that when we read an empty file, the program behaves as normal
    """

    p = PyComplete.from_text_file("tests/examples/empty.txt")
    assert p.predict("lebr") == []

def test_from_text_file_single_word():
    """
    Tests that when we read a file with a single word, the program behaves as normal
    """

    p = PyComplete.from_text_file("tests/examples/single_word.txt")
    assert p.predict("te") == []

def test_from_text_file_single_line():
    """
    Tests that when we read a file with a single line, the program behaves as normal
    """

    p = PyComplete.from_text_file("tests/examples/single_line.txt")
    assert p.predict("a") == ["a", "single"]
    assert p.predict("shoul") == ["should", "not"]

def test_from_text_file_multi_line():
    """
    Tests that when we read a file with multiple lines, the program behaves as normal
    """
    p = PyComplete.from_text_file("tests/examples/multi_line.txt")
    assert p.predict("j") == ["james", "is"]
    assert p.predict("l") == ["lebron", "james"]

def test_from_text_file_nonexistent_file_fails():
    """
    Tests that when we try to read a nonexistent file, we raise ValueError 
    """

    with pytest.raises(ValueError):
        p = PyComplete.from_text_file("tests/examples/nonexistent.txt")
    
def test_from_text_file_directory_fails():
    """
    Tests that when we try to read a directory, we raise ValueError 
    """

    with pytest.raises(ValueError):
        p = PyComplete.from_text_file("tests/examples")

# Test save and load functions
def test_save_directory_fails():
    """
    Tests that when we try to save to a directory, we get some errors
    """
    
    with pytest.raises(ValueError):
        p = PyComplete("")
        p.save("tests/examples/")

def test_load_nonexistent_fails():
    """
    Tests that when we try to load from a nonexistent file, we get some errors
    """

    with pytest.raises(ValueError):
        p = PyComplete.load("tests/examples/nonexistent.pkl")

def test_load_directory_fails():
    """
    Tests that when we try to load from a directory, we get some errors
    """

    with pytest.raises(ValueError):
        p = PyComplete.load("tests/examples/")

def test_save_load_pipeline_works():
    """
    Tests that the save -> load pipeline works
    """

    p = PyComplete("no one not two note three noted four no one no two no two no two")
    p.save("test.pkl")
    p2 = PyComplete.load("test.pkl")

    # Delete the test file now that we're done with it
    os.remove("test.pkl")

    assert p2.predict("n") == ["no", "two"]
    assert p2.predict("no") == ["no", "two"]
    assert p2.predict("not") == ["not", "two"]
    assert p2.predict("note") == ["note", "three"]
    assert p2.predict("noted") == ["noted", "four"]