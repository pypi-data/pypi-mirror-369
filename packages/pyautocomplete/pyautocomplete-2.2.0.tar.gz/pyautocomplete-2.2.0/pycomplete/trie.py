"""
This gives us the basic content for a suffix trie.

For runtime analysis purposes, we assume that the number of letters in the alphabet
is a, the number of words in the trie is n. 

TODO: THINK ABOUT RUNTIMES LOL

A lot of the walking down operations correspond to the height of the tree,
which should techincally be the length of the longest string for the uncompressed trie,
I think it should still be the same for the compressed trie.
"""

from pycomplete.trienode import TrieNode
from typing import Union

class Trie:
    def __init__(self, content: str) -> None:
        """
        TODO: think about runtime
        Assuming size of string is n. O(n) is super hard
        Builds and compresses (NOT QUITE YET) a Trie on the

        Parameters:
        ---
        content: str
            The content we are building the TrieNode structure on
        """

        words = content.split(" ")
        # Now we remove all empty strings/whitespace
        words = [word for word in words if not (word.isspace() or (len(word) == 0))]

        self._root = TrieNode("")

        for word in words:
            self.add_word(word)


    def add_word(self, word: str) -> None:
        """
        
        Adds a word to the Trie Structure. If the word already exists, do nothing.

        Parameters:
        ---
        word: str
            The word we want to add to the Trie structure
        """

        if not self.exists(word):
            curr_node = self._root

            for char in word:
                if not curr_node.exists_child(char):
                    curr_node.add_child_node(TrieNode(char))
                curr_node = curr_node.get_node(char)
            
            # NONE IS OUR END CHARACTER
            curr_node.add_child_node(TrieNode(None))
    

    def remove_word(self, word: str) -> None:
        """
        Removes `word` from the Trie structure. If the word doesn't exist in the Trie, then we raise ValueError.

        Parameters
        ---
        word: str
            The word specified
        """


        if not self.exists(word):
            raise ValueError(f"\"{word}\" does not exist within Trie")
        
        curr_node = self._walk_word(word)
        

        # Remove the node the marks the end of the word
        curr_node.remove_child(None) # type: ignore

        # NOTE: The idea is to start from the last word, removing all leaves
        # and going up the tree until we find a TrieNode with multiple children 
        while curr_node.is_leaf():  # type: ignore
            parent = curr_node.parent()  # type: ignore
            parent.remove_child_node(curr_node) # type: ignore
            curr_node = parent


    def exists(self, word: str) -> bool:
        """
        Checks if `word` exists in the Trie structure. 

        Parameters:
        ---
        word: str
            The word we want to check the existence of
        """

        node = self._walk_word(word)
        if node is None:
            return False
        
        return self._walk_word(word).exists_child(None) # type: ignore

    
    def _walk_word(self, word) -> Union[TrieNode, None]:
        """
        HELPER
        Walks down the suffix trie to find the node corresponding to the last letter of `word`

        Parameters
        ---
        word: str
            The word specified
        """

        curr_node = self._root

        for char in word:
            if curr_node.exists_child(char):
                curr_node = curr_node.get_node(char)
            else:
                return None
        
        # If there is no end word end node, then this implies
        # that there does not exist a word here
        return curr_node
    
    def _word_from(self, node: TrieNode):
        """
        HELPER
        Finds the string associated with the current node.
        
        The idea is to walk up from the current node to the root, adding str, and build from there.
        We want to be as asymptotically efficient as possible, so it's better to first add the characters to a list, 
        and then build the word from the set of characters.

        Parameters:
        ---
        node: TrieNode
            The TrideNode we want to construct the words from.
        """

        chars = []
        curr_node = node

        # Walk up the Trie, adding the letters at each node until we reach the root node
        # We add each character to a list
        while curr_node is not None:
            chars.append(curr_node.value()) # This is an O(1) operation
            curr_node = curr_node.parent()
        
        # Combine the characters in the list and reverse it
        word = "".join(chars)[::-1]
        return word

    def complete_word(self, chars: str, num: int = 2) -> list:
        """
        Finds the words closest to the sequence of characters specified in `chars`.

        Parameters
        ---
        chars: str
            The sequence of characters we want to search
        
        num: int
            The number of words we want to get. Generally speaking, the more words want to get, the longer this method will run.
            By default, we want to suggest 2 words.
        """

        curr_node = self._walk_word(chars)
        all_words = []
        num_words = 0

        # This means that we've fallen off the Trie structure 
        # This set of characters isn't in the Trie structure
        if curr_node is None:
            return []
        
        # If we're already at a word, we'd want to recommend this
        if curr_node.exists_child(None):
            all_words.append(chars)
            num_words += 1
        
        # Do a luh BFS magic until we get the appropriate number of words we want
        curr_level = curr_node.get_children_nodes()

        # Step either when we've traversed the entire tree
        # or we've collected enough enough
        while (num_words < num) and (len(curr_level) != 0):
            new_level = []
            for node in curr_level:
                # This implies that a word ends
                if node.exists_child(None):
                    all_words.append(self._word_from(node))
                    num_words += 1

                    # Stop the for loop once we get the number of suggestions 
                    if num_words == num:
                        break

                # Add all the children to the list 
                new_level += node.get_children_nodes()

            # Replace the new level
            curr_level = new_level
        

        return all_words

        

    
