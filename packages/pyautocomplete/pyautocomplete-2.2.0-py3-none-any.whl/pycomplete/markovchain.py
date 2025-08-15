"""
This is the class for a first order Markov chains.
"""

from typing import Any

class MarkovChain:
    def __init__(self) -> None: 
        """
        Initializes a first order Markov chain with an empty set of items it points towards.

        Parameters
        ---
        name: Any
            This really be anything we use to identify the content.
        """

        self._children = {}
        self._likeliest = None
        self._max_freq = 0
    
    def add_item(self, item: Any) -> None:
        """
        O(1)

        Adds an item to the Markov chain. 
        If the item already exists, then it just increments the frequency counter associated with the item by 1.

        Parameters
        ---
        item: Any
            The item we want to add to the Markov chain
        """

        if (item not in self._children):
            self._children[item] = 1
        else:
            self._children[item] += 1

        if (self._children[item] > self._max_freq):
            self._max_freq = self._children[item]
            self._likeliest = item
    

    def remove_item(self, item: Any) -> None:
        """
        O(log n) sorta kinda idk tbh

        Decreases the frequency associated with item by 1. 
        If the item already has a zero frequency associated with it, then this program does nothing.
        If the item doesn't exist, then we raise a KeyError

        Finding runtime is a bit weird here because we're assuming that each call to remove_item is equally likely
        to have any of the items as an input, so normally it'll take O(1) time, but when we call the likeliest item, it takes O(nlogn) time.
        This means the total runtime over all the inputs is O(n) + O(nlogn), which is O(nlogn), divided by n is O(logn)

        Parameters:
        ---
        item: Any
            The item we want to remove.
        """

        if (item in self._children):
            self._children[item] = max(self._children[item] - 1, 0)


            # If we decrement the likeliest item, then we want to update the most likely number
            # However, 
            if (item == self._likeliest):
                # Sort frequency in decreasing order
                self._likeliest = sorted(self._children, key=lambda elem: self._children[elem], reverse=True)[0]
                self._max_freq = self._children[self._likeliest]

                if self._max_freq == 0:
                    self._likeliest = None
        else:
            raise KeyError(f"{item} does not exist in the Markov Chain.")
    
    def likeliest(self) -> Any:
        """
        O(1)

        Returns the item with the highest frequency. 
        """

        return self._likeliest
    
    def contains(self, value: Any) -> bool:
        """
        O(1)

        Checks if the Markov chain contains `value`.

        Parameters:
        ---
        value: Any
            The value we want to search for
        """
        
        if (value in self._children):
            return self._children[value] != 0
        return False
        