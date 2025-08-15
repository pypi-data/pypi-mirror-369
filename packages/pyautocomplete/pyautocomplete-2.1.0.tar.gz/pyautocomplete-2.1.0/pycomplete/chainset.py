"""
This allows us to use and manipulate a bunch first-order Markov chains.
"""

from typing import Any
from pycomplete.markovchain import MarkovChain

class ChainSet:
    def __init__(self) -> None:
        """
        O(1)

        Initializes an empty set first-order Markov chain.
        """

        self._chains = {}
    
    def add(self, key: Any, value: Any) -> None:
        """
        O(1)

        Adds `value` to the Markov chain keyed by `key`. The Markov chain does not exist, then we create a new one.

        Parameters:
        ---
        key: Any
            The key of the Markov chain.
        
        value: Any
            The value we want to add 
        """

        if key not in self._chains:
            self.create_chain(key)

        self._chains[key].add_item(value)
            
    
    def create_chain(self, key: Any) -> None:
        """
        O(1)

        Creates a new Markov chain with a specific name. Raises ValueError if the key exists

        Parameters:
        ---
        key: Any
            The key of the Markov chain.
        """

        if key not in self._chains:
            self._chains[key] = MarkovChain()
        else:
            raise ValueError(f"Key \"{key}\" already exists")
    
    def remove(self, key: Any, value: Any) -> None:
        """
        O(1)

        Decrements an the frequency associated with value associated with the given key.

        Parameters:
        ---
        key: Any
            The key of the Markov chain.
        
        value: Any
            The value we want to remove 
        """

        if key not in self._chains:
            raise ValueError(f"Key \"{key}\" does not exist.")
        
        if not self._chains[key].contains(value):
            raise ValueError(f"Markov chain does not contain  \"{value}\"")
        
        self._chains[key].remove_item(value)
    

    def exists(self, key: Any) -> bool:
        """
        O(1)

        Checks if the key exists in the set of chains

        Parameters:
        ---
        key: Any
            The key to the Markov chain
        """

        return key in self._chains
    
    def likeliest(self, key: Any) -> Any:
        """
        O(1)

        Gets the likeliest value to occur given `key` occured. Raises ValueError if key doesn't exist.

        Parameters:
        ---
        key: Any
            The key to the Markov chain
        """
        
        if key not in self._chains:
            raise ValueError(f"\"{key}\" does not exist.")
        
        return self._chains[key].likeliest()