"""
Now we're putting all the helper classes together in order to get the PyComplete module.

TODO: find out runtimes lol (should largely come from pycomplete/trie.py)
"""

from pycomplete.chainset import ChainSet
from pycomplete.trie import Trie
import os
import pickle

class PyComplete:
    def __init__(self, text: str) -> None:
        """
        Initializes an instance of PyComplete, which builds a Trie and develops the set of first-order Markov
        chains on the text given


        Parameters
        ---
        text: str
            String containing the body of text we're trying to run PyComplete on
        """

        words = text.split(" ")
        self._chains = ChainSet()
        self._trie = Trie("")

        # Now we remove all empty strings/whitespace
        words = [word for word in words if not (word.isspace() or (len(word) == 0))]

        self._word_count = len(words)

        for index, word in enumerate(words):
            # If we're not at the second to last word
            if (index != len(words) - 1):
                self._chains.add(word, words[index+1])
            self._trie.add_word(word)
    
    def predict(self, text: str, num: int = 1) -> list:
        """
        Predicts what the completed word (and following word) given a sequence of characters.
        Returns a list containing the completed word, followed by the words after it.

        if num < 1, we raise ValueError.

        Parameters
        ---
        text: str
            The given sequence of characters

        num: int
            How many words ahead do we want to predict. By default, we predict one word ahead. Now, if we get at a word
            that doesn't have any following words after it, then we return the list of predictions, even if it's less
            than `num`
        """

        if num < 1:
            raise ValueError(f"num: \"{num}\" is less than 1")

        # Ain't nun to predict if we don't have any words
        if self._word_count == 0:
            return []
    
        if self._word_count == 1:
            return []
        
        result = []
        completed_words = self._trie.complete_word(text.strip(), num=1)

        # This implies `text` is NOT within the trie.
        if (completed_words == []):
            return [text.strip()]
        
        result.append(completed_words[0])

        # Keep predicting further ahead until we either get an error 
        # (this implies that the completed/predicted word doesn't have any following characters)
        # or we don't need to predict any further ahead 
        try:
            for i in range(0, num):
                result.append(self._chains.likeliest(result[i]))
        except ValueError:
            return result

        return result
    
    def add_pair(self, key: str, value: str) -> None:
        """
        Adds a pair of words to the Markov chain.

        Parameters
        ---
        key: str
            The first word in the pair we want to add
        
        value: str
            The second word in the pair
        """
        # Ensure the word exiss in the Trie for future predictions
        # also increment word count
        if not self._trie.exists(key):
            self._trie.add_word(key)
        
        if not self._trie.exists(value):
            self._trie.add_word(value)
        
        # We're techincally incremening the word count
        self._word_count += 2
        
        # Then we add it to the ChainSet
        self._chains.add(key, value)
    

    def add_line(self, line: str) -> None:
        """
        Adds an entire line of text

        Parameters
        ---
        line: str
            The line we want to add to the autocomplete system
        """

        # Now we remove all empty strings/whitespace from the line
        words = line.split(" ")
        words = [word for word in words if not (word.isspace() or (len(word) == 0))]

        self._word_count += len(words)

        for index, word in enumerate(words):
            # If we're not at the second to last word
            if (index != len(words) - 1):
                self._chains.add(word, words[index+1])
            self._trie.add_word(word)
    
    def save(self, filepath: str) -> None:
        """
        Saves the current PyComplete instance as a file. Raises ValueError if we're filepath is a directory.

        Parameters
        ---
        filepath: str
            The path to the file we want to handle
        """

        if os.path.exists(filepath) and os.path.isdir(filepath):
            raise ValueError(f"Path \"{filepath}\" is a directory.")

        with open(filepath, "wb") as f:
            pickle.dump(self, f)
    

    @staticmethod
    def from_text_file(filepath: str) -> "PyComplete":
        """
        Extracts the text from the file specified in the filepath and returns a PyComplete instance generated
        from that text. We raise ValueError if the file we're reading is a directory or simply doesn't exist.

        Parameters
        ---
        filepath: str
            The path to the file we want to read
        """

        p = PyComplete("") # This should be an O(1) operation

        if not os.path.exists(filepath):
            raise ValueError(f"Path \"{filepath}\" does not exist")
        
        if os.path.isdir(filepath):
            raise ValueError(f"Path \"{filepath}\" is a directory.")
        
        # Build the 
        with open(filepath, "r") as f:
            for line in f:
                p.add_line(line.strip())
        
        return p
    
    @staticmethod
    def load(filepath: str) -> "PyComplete":
        """
        Loads the PyComplete instance from the path. Raises ValueError if filepath is a directory.

        Parameters
        ---
        filepath: str
            The path to the file we want to read
        """

        if not os.path.exists(filepath):
            raise ValueError(f"Path \"{filepath}\" does not exist")
        
        if os.path.isdir(filepath):
            raise ValueError(f"Path \"{filepath}\" is a directory")
    
        with open(filepath, "rb") as f:
            return pickle.load(f)
