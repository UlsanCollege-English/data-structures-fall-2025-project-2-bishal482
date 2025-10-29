"""
Trie data structure for autocomplete.

Public surface expected by tests:
- class Trie
  - insert(word: str, freq: float) -> None
  - removeremove(word: str) -> bool
  - contains(word: str) -> bool
  - complete(prefix: str, k: int) -> list[str]
  - stats() -> tuple[int, int, int]  # (words, height, nodes)
  - items() -> list[tuple[str, float]] # Helper for saving

Complexity target (justify in docstrings):
- insert/remove/contains: O(len(word))
- complete(prefix, k): roughly O(m + k log k')
"""

import heapq # For efficient top-k selection

class TrieNode:
    """
    A single node in the Trie.
    
    __slots__ is used to reduce memory footprint by preventing the creation
    of a __dict__ for each node.
    """
    __slots__ = ("children", "is_word", "freq")

    def __init__(self):
        # Dictionary mapping character -> TrieNode
        self.children = {}
        # Boolean flag indicating if a word ends at this node
        self.is_word = False
        # Frequency score of the word. 0.0 if not a word.
        self.freq = 0.0

class Trie:
    def __init__(self):
        """
        Initializes an empty Trie.
        """
        self.root = TrieNode()
        self._words = 0
        self._nodes = 1 # Start with 1 node (the root)

    def _find_node(self, word):
        """
        Helper: Traverses the Trie to find the node corresponding
        to the end of the given word (or prefix).
        Returns: The (TrieNode, path_nodes) or (None, []) if not found.
        """
        cur = self.root
        path_nodes = [(cur, '')] # Store (node, char) for removal pruning
        for char in word:
            if char not in cur.children:
                return None, []
            cur = cur.children[char]
            path_nodes.append((cur, char))
        return cur, path_nodes

    def insert(self, word, freq):
        """
        Inserts a word into the Trie with its associated frequency.
        If the word already exists, its frequency is updated.

        Complexity: O(L) where L is the length of the word.
        We traverse the Trie, visiting at most L nodes. Dictionary
        lookups/insertions (self.children) are O(1) on average.
        """
        cur = self.root
        for char in word:
            if char not in cur.children:
                # Create a new node if path doesn't exist
                cur.children[char] = TrieNode()
                self._nodes += 1
            cur = cur.children[char]
        
        # Mark the end of a word
        if not cur.is_word:
            self._words += 1
            cur.is_word = True
        
        # Update frequency
        cur.freq = freq

    def remove(self, word):
        """
        Removes a word from the Trie. Returns True if the word
        was successfully removed, False if the word was not found.
        This operation prunes (removes) nodes that are no longer
        part of any word.

        Complexity: O(L) where L is the length of the word.
        We first traverse O(L) to find the word. Then, we
        traverse back up O(L) to prune nodes.
        """
        node, path_nodes = self._find_node(word)

        # Case 1: Word not found or is not a word
        if not node or not node.is_word:
            return False

        # Case 2: Word is found and is a word
        node.is_word = False
        node.freq = 0.0
        self._words -= 1

        # Case 3: Prune nodes if they are no longer needed
        # Iterate backwards from the parent of the removed word's node
        for i in range(len(path_nodes) - 1, 0, -1):
            parent_node, char = path_nodes[i-1]
            current_node, _ = path_nodes[i]

            # If current_node has no children and is not a word,
            # it can be removed from its parent.
            if not current_node.children and not current_node.is_word:
                # Safety check: only delete if char is actually in children
                # This prevents a KeyError if logic is ever flawed.
                if char in parent_node.children:
                    del parent_node.children[char]
                    self._nodes -= 1
            else:
                # If the node is still in use (has children or is
                # another word), stop pruning.
                break
        
        return True

    def contains(self, word):
        """
        Checks if the exact word exists in the Trie.

        Complexity: O(L) where L is the length of the word.
        We traverse the Trie, visiting at most L nodes.
        """
        node, _ = self._find_node(word)
        return node is not None and node.is_word

    def complete(self, prefix, k):
        """
        Finds all words in the Trie starting with the given prefix,
        ranked by frequency (highest first). Ties are broken
        lexicographically (alphabetically).

        Complexity: O(M + N log K), where:
        - M is the length of the prefix (to find the prefix node).
        - N is the number of words reachable from the prefix node.
        - K is the number of suggestions requested.
        We use a min-heap of size K to store the top-K items.
        - Finding the prefix node is O(M).
        - The recursive search _collect_all visits every node
          and word in the subtree (O(N nodes/words)).
        - For each of the N words, we do a heap operation (push/pop)
          which is O(log K).
        - The final sort is O(K log K).
        
        This is faster than O(M + N log N) if K is much smaller than N.
        """
        node, _ = self._find_node(prefix)
        if not node:
            return []

        # Use a min-heap to keep track of the top K
        # We store (frequency, word). The heap prioritizes the
        # smallest frequency, so we can pop it when we find
        # a word with a higher frequency.
        top_k_heap = []

        def _collect_all(current_node, current_word):
            """
            Recursively explore from current_node, building
            current_word, and add results to top_k_heap.
            """
            if current_node.is_word:
                # We store (freq, word) to sort by freq.
                # heapq is a min-heap, so if heap is full,
                # we push the new item then pop the smallest.
                item = (current_node.freq, current_word)
                if len(top_k_heap) < k:
                    heapq.heappush(top_k_heap, item)
                else:
                    # push and pop in one step
                    heapq.heappushpop(top_k_heap, item)

            # Recurse for all children, sorted alphabetically
            # to ensure lexicographic tie-breaking.
            for char, child_node in sorted(current_node.children.items()):
                _collect_all(child_node, current_word + char)

        # Start the collection from the prefix node
        _collect_all(node, prefix)

        # The heap now contains the top K items, but they are
        # (freq, word) and sorted by freq ascending.
        # We need to sort them by freq descending, and for ties,
        # by word ascending (lexicographically).
        
        # Sort by frequency (descending) then word (ascending)
        # -x[0] for descending freq, x[1] for ascending word
        sorted_results = sorted(top_k_heap, key=lambda x: (-x[0], x[1]))
        
        # Return only the words
        return [word for freq, word in sorted_results]

    def stats(self):
        """
        Returns statistics about the Trie.
        - words: Total number of words stored.
        - height: The length of the longest word.
        - nodes: Total number of TrieNodes.

        Complexity: O(T) where T is the total number of nodes.
        We must traverse all nodes to find the height.
        """
        
        def _get_height(node):
            """Recursive helper to find max depth."""
            if not node.children:
                return 0
            
            # Height of this node is 1 + max height of its children
            max_child_height = 0
            for child in node.children.values():
                max_child_height = max(max_child_height, _get_height(child))
            
            # The +1 accounts for the current edge/char
            return 1 + max_child_height

        # _words and _nodes are tracked in O(1)
        # height must be calculated
        height = _get_height(self.root)
        
        return (self._words, height, self._nodes)

    def items(self):
        """
        Helper for 'save' command. Returns a list of all
        (word, freq) pairs in the Trie.
        
        Complexity: O(T) where T is the total number of nodes,
        as we must visit every node.
        """
        all_items = []
        def _collect(node, current_word):
            if node.is_word:
                all_items.append((current_word, node.freq))
            
            for char, child_node in node.children.items():
                _collect(child_node, current_word + char)
        
        _collect(self.root, "")
        return all_items

