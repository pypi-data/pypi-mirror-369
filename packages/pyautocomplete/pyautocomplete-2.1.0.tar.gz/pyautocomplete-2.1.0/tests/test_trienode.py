"""
Test pycomplete/trienode.py
"""

from pycomplete.trienode import TrieNode
import pytest

# TEST: init and getters
def test_trienode_num_children():
    """
    Test that when we initialize the TrieNode we have zero children.
    """

    tn = TrieNode("t")
    assert tn.num_children() == 0

def test_trienode_parent_none():
    """
    Tests that when we initialize the TrieNode, we have no children
    """

    tn = TrieNode("t")
    assert tn.parent() == None

def test_trienode_parent_get_value():
    """
    Tests that when we initialize the TrieNode, our value remains consistent
    with the argument specified
    """

    tn = TrieNode("t")
    assert tn.value() == "t"

def test_trienode_isleaf():
    """
    Tests that when we initialize the TrieNode, it initializes as a leaf
    """

    tn = TrieNode("t")
    assert tn.is_leaf()

# TEST: set_parent
def test_trienode_set_parent():
    """
    Tests that we can use set_parent to properly change the parent 
    """

    tn = TrieNode("t")
    p = TrieNode("parent")
    tn.set_parent(p)
    assert tn.parent() == p


# TEST: add_child_node
def test_add_child_node_exists():
    """
    Tests that when we add a child node, it actually exists

    (this has the effect of also testing the exists_child method)
    """

    tn = TrieNode("t")
    c = TrieNode("child1")
    tn.add_child_node(c)
    assert tn.exists_child("child1")

def test_add_child_node_child_parent_works():
    """
    Tests that when we add a child node, the child node's parent is acutally the parent node

    (this has the effect of also testing the exists_child method)
    """

    tn = TrieNode("t")
    c = TrieNode("child1")
    tn.add_child_node(c)
    assert c.parent() == tn

def test_add_existing_child_fails():
    """
    Tests that when we add a child node that already exists, we get ValueError
    """

    with pytest.raises(ValueError):
        tn = TrieNode("t")
        tn.add_child_node(TrieNode("child1"))
        tn.add_child_node(TrieNode("child1"))

def test_add_existing_child_increments_num_children():
    """
    Tests that when we add a child node, we increment the number of children
    """
    tn = TrieNode("t")
    tn.add_child_node(TrieNode("c1"))
    tn.add_child_node(TrieNode("c2"))
    assert tn.num_children() == 2


# TEST: remove_child_node
def test_remove_child_node():
    """
    Tests that when we remove a child node, it acutally doesn't exist

    (also has the effect of testing exists_child)
    """

    tn = TrieNode("t")
    c1 = TrieNode("c1")
    tn.add_child_node(c1)
    tn.remove_child_node(c1)
    assert not tn.exists_child("c1")

def test_remove_child_node_fails_when_child_not_exist():
    """
    Tests that when we remove a child node that doesn't exist, we raise ValueError.
    """

    with pytest.raises(ValueError):
        tn = TrieNode("t")
        c = TrieNode("c1")
        tn.remove_child_node(c)

def test_remove_child_node_fails():
    """
    Tests that when we remove a child node, the number of children decreases
    """

    tn = TrieNode("t")
    c1 = TrieNode("c1")
    c2 = TrieNode("c2")
    tn.add_child_node(c1)
    tn.add_child_node(c2)
    tn.remove_child_node(c2)
    assert tn.num_children() == 1

def test_remove_child_node_return():
    """
    Tests that removing the child node returns the node we removed
    """

    tn = TrieNode("t")
    c1 = TrieNode("c1")
    c2 = TrieNode("c2")
    tn.add_child_node(c1)
    tn.add_child_node(c2)
    assert tn.remove_child_node(c2) == c2

# TEST: remove_child
def test_remove_child():
    """
    Tests that when we remove a child node, it acutally doesn't exist

    (also has the effect of testing exists_child)
    """

    tn = TrieNode("t")
    c1 = TrieNode("c1")
    tn.add_child_node(c1)
    tn.remove_child("c1")
    assert not tn.exists_child("c1")

def test_remove_child_fails_when_child_not_exist():
    """
    Tests that when we remove a child node that doesn't exist, we raise ValueError.
    """

    with pytest.raises(ValueError):
        tn = TrieNode("t")
        tn.remove_child("c1")

def test_remove_child_fails():
    """
    Tests that when we remove a child node, the number of children decreases
    """

    tn = TrieNode("t")
    c1 = TrieNode("c1")
    c2 = TrieNode("c2")
    tn.add_child_node(c1)
    tn.add_child_node(c2)
    tn.remove_child("c2")
    assert tn.num_children() == 1

def test_remove_child_return():
    """
    Tests that removing the child node returns the node we removed
    """

    tn = TrieNode("t")
    c1 = TrieNode("c1")
    c2 = TrieNode("c2")
    tn.add_child_node(c1)
    tn.add_child_node(c2)
    assert tn.remove_child("c2") == c2

# TEST: exists_child
def test_exists_child_false():
    """
    Tests that exists_child gives false. We already tested that exists_child works earlier; 
    """

    tn = TrieNode("t")
    c = TrieNode("c2")
    tn.add_child_node(c)
    assert not tn.exists_child("c1")


# TEST: get_node
def test_get_node_fails_with_nonexistent():
    """
    Tests that when we call get_node on a non-existent node, we get failure
    """

    with pytest.raises(ValueError):
        tn = TrieNode("t")
        tn.get_node("c1")

def test_get_node_works():
    """
    Tests that get_node works on an existing node
    """

    tn = TrieNode("t")
    c = TrieNode("c")
    tn.add_child_node(c)
    assert tn.get_node("c") == c

# TEST: get_children_values
def test_get_children_values_works_empty():
    """
    Tests that getting the children nodes of a TrieNode with no children 
    gives us an empty list
    """

    tn = TrieNode("t")
    assert len(tn.get_children_values()) == 0

def test_get_children_values_singleton():
    """
    Tests that getting the children nodes of a TrieNode with no children 
    gives us a list with a single item
    """
     
    tn = TrieNode("t")
    tn.add_child_node(TrieNode("c"))
    assert tn.get_children_values() == ["c",]

def test_get_children_values_multiple_items():
    """
    Tests that getting the children nodes of a TrieNode with no children 
    gives us a list with a single item
    """
     
    tn = TrieNode("t")
    tn.add_child_node(TrieNode("c"))
    tn.add_child_node(TrieNode("c2"))
    tn.add_child_node(TrieNode("c3"))
    assert set(tn.get_children_values()) == {"c", "c2", "c3"}

# TEST: get_children_nodes
def test_get_children_nodes_works_empty():
    """
    Tests that getting the children nodes of a TrieNode with no children 
    gives us an empty list
    """

    tn = TrieNode("t")
    assert len(tn.get_children_nodes()) == 0

def test_get_children_nodes_singleton():
    """
    Tests that getting the children nodes of a TrieNode with no children 
    gives us a list with a single item
    """
     
    tn = TrieNode("t")
    c = TrieNode("c")
    tn.add_child_node(c)
    assert tn.get_children_nodes() == [c,]

def test_get_children_nodes_multiple_items():
    """
    Tests that getting the children nodes of a TrieNode with no children 
    gives us a list with a single item
    """
     
    tn = TrieNode("t")
    c = TrieNode("c")
    c2 = TrieNode("c2")
    c3 = TrieNode("c3")
    tn.add_child_node(c)
    tn.add_child_node(c2)
    tn.add_child_node(c3)
    assert set(tn.get_children_nodes()) == {c, c2, c3}