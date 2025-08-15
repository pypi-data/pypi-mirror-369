"""
Test pycomplete/trie.py
"""

from pycomplete.trie import Trie
import pytest

# Test initialization (likely will test some other functions too)
# TEST: exists
def test_no_words():
    """
    Tests that when we initialize a Trie with no words, we actually get no words
    """

    t = Trie("")
    assert not t.exists("")
    assert not t.exists("lebron")

def test_single_word():
    """
    Tests that when we initialize a Trie with a single word, we get only a single word
    """
    t = Trie("lebron")
    assert t.exists("lebron")
    assert not t.exists("")
    assert not t.exists("goat")


def test_multiple_words():
    """
    Tests that when we add multiple words, we only get those words and nothing else
    """

    t = Trie("lebron james is the goat")
    assert t.exists("lebron")
    assert t.exists("james")
    assert t.exists("is")
    assert not t.exists('not')
    assert t.exists("the")
    assert t.exists("goat")

def test_words_on_same_walk():
    """
    Tests that when we add words on the same walk on the Trie, nothing funky happens
    """

    t = Trie("noted")
    assert t.exists("noted")
    assert not t.exists("n")
    assert not t.exists("no")
    assert not t.exists('not')
    assert not t.exists('note')


# TEST: add_word 
def test_add_word_works():
    """
    Tests that add word ensures the word exists
    """

    t = Trie("lebron")

    assert t.exists("lebron")
    assert not t.exists("james")
    t.add_word("james")
    assert t.exists("james")

def test_add_existing_word_does_nothing():
    """
    Tests that add word to an existing set does nothing
    """

    t = Trie("lebron")

    assert t.exists("lebron")
    assert not t.exists("james")
    t.add_word("james")
    t.add_word("lebron")
    assert t.exists("james")
    assert t.exists("lebron")

# TEST: remove_word
def test_remove_single_word_works():
    """
    Tests that when we remove a word, it actually gets removed
    """

    t = Trie("lebron james is not the goat")
    t.remove_word("not")
    assert t.exists("lebron")
    assert t.exists("james")
    assert t.exists("is")
    assert not t.exists("not")
    assert t.exists("the")
    assert t.exists("goat")

def test_remove_multiple_words_works():
    """
    Tests that when we remove multiple words, they get removed.
    """

    t = Trie("lebron james is not note noted the goat")
    t.remove_word("not")
    assert t.exists("lebron")
    assert t.exists("james")
    assert t.exists("is")
    assert not t.exists("not")
    assert t.exists("note")
    assert t.exists("noted")
    assert t.exists("the")
    assert t.exists("goat")

    t.remove_word("noted")
    assert t.exists("lebron")
    assert t.exists("james")
    assert t.exists("is")
    assert not t.exists("not")
    assert t.exists("note")
    assert not t.exists("noted")
    assert t.exists("the")
    assert t.exists("goat")

    t.remove_word("note")
    assert t.exists("lebron")
    assert t.exists("james")
    assert t.exists("is")
    assert not t.exists("not")
    assert not t.exists("note")
    assert not t.exists("noted")
    assert t.exists("the")
    assert t.exists("goat")

    t.remove_word("lebron")
    assert not t.exists("lebron")
    assert t.exists("james")
    assert t.exists("is")
    assert not t.exists("not")
    assert not t.exists("note")
    assert not t.exists("noted")
    assert t.exists("the")
    assert t.exists("goat")

def test_remove_nonexistent_word_fails():
    """
    Tests that when we remove a nonexistent word, we raise ValueError
    """

    with pytest.raises(ValueError):
        t = Trie("lebron james is the goat")
        t.remove_word("not")

# TEST: complete_word
def test_complete_empty_gives_empty():
    """
    Tests that running complete on an empty Trie
    """

    t = Trie("")
    assert len(t.complete_word("lebron")) == 0

def test_complete_works_normal():
    """
    Tests that running works on normal use cases
    """

    t = Trie("no note noted noteds")
    assert set(t.complete_word("no")) == {"no", "note"}

def test_complete_works_normal2():
    """
    Tests that running works on normal use cases
    """

    t = Trie("lebron james is truly the greatest")
    assert set(t.complete_word("t")) == {"truly", "the"}
    assert set(t.complete_word("l")) == {"lebron"}
    assert set(t.complete_word("j")) == {"james"}
    assert set(t.complete_word("i")) == {"is"}
    assert set(t.complete_word("gre")) == {"greatest"}

def test_complete_only_one_word():
    """
    Tests that complete_word works with a single word
    """

    t = Trie("noted")
    assert set(t.complete_word("no")) == {"noted"}

def test_complete_not_work_nonexisting():
    """
    Tests that we get an empty  list
    """

    t = Trie("this test has been duly noted")
    assert len(t.complete_word("lebron")) == 0
