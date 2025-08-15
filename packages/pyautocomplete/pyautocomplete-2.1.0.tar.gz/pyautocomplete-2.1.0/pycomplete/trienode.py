"""
This allows us to create and manipulate Nodes within the Trie structure.

We're assuming that the value of the Node within a specific alphabet.
This implies that a certain TrieNode should NOT have a child.

For runtime analysis purposes, we're assuming that n = the number of children in the TrieNode.
"""

from typing import Union, Any

class TrieNode:
    def __init__(self, value: Any, parent: Union["TrieNode", None] = None) -> None:
        """
        O(1)

        Initializes a TrieNode instance with no children.

        Parameters:
        ---
        value: Any
            The value of the new TrieNode
        
        parent: TrieNode | None
            The parent of the current TrieNode
        """

        self._value = value
        self._parent = parent

        self._children = {}
        self._num_children = 0
    
    def set_parent(self, new_parent: Union["TrieNode", None]) -> None:
        """
        O(1)

        Sets the parent `new_parent`

        Parameters:
        ---
        new_parent: Any
            The new parent we want to set
        """

        self._parent = new_parent
    
    def parent(self) -> Union["TrieNode", None]:
        """
        O(1)

        Returns the parent
        """

        return self._parent
    
    def add_child_node(self, child: "TrieNode") -> None:
        """
        O(1)

        Adds a child node to this current node. It also automatically sets the parent of
        this node to this node too. If the child TrieNode already exists, we raise ValueError.

        Parameters
        ---
        child: TrieNode
            The child TrieNode we want to add
        """

        if child._value in self._children:
            raise ValueError("Child TrieNode already exists")
        
        self._children[child._value] = child
        child._parent = self
        self._num_children += 1

    def remove_child_node(self, child: "TrieNode") -> "TrieNode":
        """
        O(1)

        Removes `child` from set of children. It also sets the parent of `child` to None. 
        Returns the child that we removed.
        Raises ValueError if `child` is not a child of the TrieNode

        Parameters
        ---
        child: TrieNode
            The child TrieNode we want to remove
        """

        if child._value not in self._children:
            raise ValueError("Child does not exist")
        
        child._parent = None
        self._num_children = max(self._num_children - 1, 0)
        return self._children.pop(child._value)

    def remove_child(self, value: Any) -> "TrieNode":
        """
        O(1)

        Removes `value` from the set of children. It also sets the parent of the child
        associated to `value` to None. Returns the child TrieNode we removed.

        Parameters
        ---
        value: Any
            The value we want to remove
        """

        if value not in self._children:
            raise ValueError("Child does not exist")
        
        self._children[value]._parent = None
        self._num_children = max(self._num_children - 1, 0)
        return self._children.pop(value)
    

    def exists_child(self, value: Any) -> bool:
        """
        O(1)

        Checks if a value exists within a child

        Parameters
        ---
        value: Any
            The value we want to check the existence of
        """

        return value in self._children

    def get_node(self, value: Any) -> "TrieNode":
        """
        O(1)

        Returns the TrieNode corresponding to the value. If there is no child corresponding to value, 
        we raise ValueError.

        Parameters
        ---
        value: Any
            The value we want to extract
            
        """
        if value not in self._children:
            raise ValueError(f"\"{value}\" does not exist as a child")
        return self._children[value]


    def get_children_values(self) -> list:
        """
        O(n)

        Returns all the values of the children Nodes 
        """

        return list(self._children.keys())
    

    def get_children_nodes(self) -> list:
        """
        O(n)

        Returns all the children Nodes 
        """

        return list(self._children.values())


    def is_leaf(self) -> bool:
        """
        O(1)

        Returns whether this current node is a leaf or not.
        """
        return self._num_children == 0

    def num_children(self) -> int:
        """
        O(1)

        Returns the number of children the TrieNode has
        """

        return self._num_children

    def value(self) -> Any:
        """
        O(1)

        Returns the current value of this TrieNode
        """

        return self._value
    
    def __str__(self) -> str:
        return str(self._value)