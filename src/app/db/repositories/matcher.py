import os
import re
from typing import List, Dict, Union
import fitz

# SOURCE : https://www.geeksforgeeks.org/dsa/aho-corasick-algorithm-pattern-searching/
class AhoCorasick:
    def __init__(self, words):

        # Max number of states in the matching machine.
        # Should be equal to the sum of the length of all keywords.
        self.max_states = sum([len(word) for word in words])

        # Maximum number of characters.
        # Currently supports only alphabets [a,z]
        self.max_characters = 37

        # OUTPUT FUNCTION IS IMPLEMENTED USING out []
        # Bit i in this mask is 1 if the word with
        # index i appears when the machine enters this state.
        # Lets say, a state outputs two words "he" and "she" and
        # in our provided words list, he has index 0 and she has index 3
        # so value of out[state] for this state will be 1001
        # It has been initialized to all 0.
        # We have taken one extra state for the root.
        self.out = [0]*(self.max_states+1)

        # FAILURE FUNCTION IS IMPLEMENTED USING fail []
        # There is one value for each state + 1 for the root
        # It has been initialized to all -1
        # This will contain the fail state value for each state
        self.fail = [-1]*(self.max_states+1)

        # GOTO FUNCTION (OR TRIE) IS IMPLEMENTED USING goto [[]]
        # Number of rows = max_states + 1
        # Number of columns = max_characters i.e 26 in our case
        # It has been initialized to all -1.
        self.goto = [[-1]*self.max_characters for _ in range(self.max_states+1)]
        
        # Convert all words to lowercase
        # so that our search is case insensitive
        for i in range(len(words)):
          words[i] = words[i].lower()
          
        # All the words in dictionary which will be used to create Trie
        # The index of each keyword is important:
        # "out[state] & (1 << i)" is > 0 if we just found word[i]
        # in the text.
        self.words = words

        # Once the Trie has been built, it will contain the number
        # of nodes in Trie which is total number of states required <= max_states
        self.states_count = self.__build_matching_machine()


    # Builds the String matching machine.
    # Returns the number of states that the built machine has.
    # States are numbered 0 up to the return value - 1, inclusive.
    def __build_matching_machine(self):
        k = len(self.words)

        # Initially, we just have the 0 state
        states = 1

        # Convalues for goto function, i.e., fill goto
        # This is same as building a Trie for words[]
        for i in range(k):
            word = self.words[i]
            current_state = 0

            # Process all the characters of the current word
            for character in word:
                ch = None
                if (character.isalpha()):
                    ch = ord(character.lower()) - 97
                elif (character.isdigit()):
                    ch = ord(character) - 22

                # Allocate a new node (create a new state)
                # if a node for ch doesn't exist.
                if self.goto[current_state][ch] == -1:
                    self.goto[current_state][ch] = states
                    states += 1

                current_state = self.goto[current_state][ch]

            # Add current word in output function
            self.out[current_state] |= (1<<i)

        # For all characters which don't have
        # an edge from root (or state 0) in Trie,
        # add a goto edge to state 0 itself
        for ch in range(self.max_characters):
            if self.goto[0][ch] == -1:
                self.goto[0][ch] = 0
        
        # Failure function is computed in 
        # breadth first order using a queue
        queue = []

        # Iterate over every possible input
        for ch in range(self.max_characters):

            # All nodes of depth 1 have failure
            # function value as 0. For example,
            # in above diagram we move to 0
            # from states 1 and 3.
            if self.goto[0][ch] != 0:
                self.fail[self.goto[0][ch]] = 0
                queue.append(self.goto[0][ch])

        # Now queue has states 1 and 3
        while queue:

            # Remove the front state from queue
            state = queue.pop(0)

            # For the removed state, find failure
            # function for all those characters
            # for which goto function is not defined.
            for ch in range(self.max_characters):

                # If goto function is defined for
                # character 'ch' and 'state'
                if self.goto[state][ch] != -1:

                    # Find failure state of removed state
                    failure = self.fail[state]

                    # Find the deepest node labeled by proper
                    # suffix of String from root to current state.
                    while self.goto[failure][ch] == -1:
                        failure = self.fail[failure]
                    
                    failure = self.goto[failure][ch]
                    self.fail[self.goto[state][ch]] = failure

                    # Merge output values
                    self.out[self.goto[state][ch]] |= self.out[failure]

                    # Insert the next level node (of Trie) in Queue
                    queue.append(self.goto[state][ch])
        
        return states


    # Returns the next state the machine will transition to using goto
    # and failure functions.
    # current_state - The current state of the machine. Must be between
    #             0 and the number of states - 1, inclusive.
    # next_input - The next character that enters into the machine.
    def __find_next_state(self, current_state, next_input):
        answer = current_state
        ch = None
        if (next_input.isalpha()):
            ch = ord(next_input.lower()) - 97
        elif (next_input.isdigit()):
            ch = ord(next_input) - 22
        else:
            ch = 36

        # If goto is not defined, use
        # failure function
        while self.goto[answer][ch] == -1:
            answer = self.fail[answer]

        return self.goto[answer][ch]


    # This function finds all occurrences of all words in text.
    def search_words(self, text) -> Dict:
        # Convert the text to lowercase to make search case insensitive

        # Initialize current_state to 0 
        current_state = 0

        # A dictionary to store the result.
        # Key here is the found word
        # Value is a list of all occurrences start index
        results = [0] * len(self.words)

        # Traverse the text through the built machine
        # to find all occurrences of words
        for i in range(len(text)):
            current_state = self.__find_next_state(current_state, text[i])

            # If match not found, move to next state
            if self.out[current_state] == 0: continue

            # Match found, store the word in result dictionary
            for j in range(len(self.words)):
                if (self.out[current_state] & (1<<j)) > 0:
                    results[j] += 1

        total_queries = len(self.words)
        queries = self.words

        # Return the final result dictionary
        return {
            'total_queries': total_queries,
            'query': queries,
            'matched_queries': results,
            'method_used': "Aho-Corasick",
        }

class Matcher:
    def __init__(self, cv_paths: List[str], queries: List[str]):
        self.cv_paths = cv_paths
        self.texts = []
        self.automaton_trie = None

        self.queries = [query.lower() for query in queries]

        for path in self.cv_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
            self.texts.append(self.extract_text(path, 0))


    def extract_text(self, path: str, case: int) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        file_ext = os.path.splitext(path)[1].lower()
        text = ""
        
        try:
            if file_ext == '.pdf':
                text = self._extract_from_pdf(path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            result = text.lower() if case == 0 else text
            print(f"Finished extracting text ({'lowercase' if case == 0 else 'original case'})")
            return result
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
        
    def _get_important_information(self, text: str) -> Dict[str, Union[str, List[str]]]:
        """Extract important information from the text"""
        # TODO using REGEX
        return {
            "name": "",
            "birth_date": "",
            "address": "",
            "email": "",
            "phone": "",
            "skills": [],
            "education": [],
            "experience": []
        }

    def _extract_from_pdf(self, path: str) -> str:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    
    def match(self, method: str, threshold: float = 0.8) -> Dict:
        if not self.queries:
            raise ValueError("Queries list is empty")
    
        result = []    
        for text in self.texts:
            if method == 'exact':
                result.append(self._exact_match(text, self.queries))
            elif method == 'KMP':
                result.append(self._KMP_match(text, self.queries))
            elif method == 'BM':
                result.append(self._BM_match(text, self.queries))
            elif method == 'AC':
                # TODO: Implement Aho-Corasick algorithm

                if (self.automaton_trie is None):
                    # build the automaton trie here
                    automaton_trie = AhoCorasick(self.queries)
                result.append(automaton_trie.search_words(text))
            elif method == 'fuzzy':
                result.append(self._fuzzy_match(text, self.queries, threshold))
            else:
                raise ValueError(f"Unsupported matching method: {method}")
        return result

    def _exact_match_1_query(self, text:str, query: str) -> Dict:  
        matches = []
        count = 0
        start = 0
        
        while True:
            pos = text.find(query, start)
            if pos == -1:
                break
            matches.append(pos)
            count += 1
            start = pos + 1
        
        return count
    
    def _exact_match(self, text:str, queries: List[str]) -> Dict:
        results = []
        for query in queries:
            result = self._exact_match_1_query(text, query)
            results.append(result)

        total_queries = len(queries)

        return {
            'total_queries': total_queries,
            'query': queries,
            'matched_queries': results,
            'method_used': "exact",
        }
    
    def _KMP_match_1_query(self, text:str, query: str) -> List:
        """ KMP algorithm to find all occurrences of a query in the extracted text """
        """ source : https://cp-algorithms.com/string/prefix-function.html """

        s = query + "#" + text
        n = len(text)
        m = len(query)
        pi = [0] * n
        occ = []

        count = 0

        for i in range(1, n):
            j = pi[i - 1]
            while j > 0 and s[i] != s[j]:
                j = pi[j - 1]
            if s[i] == s[j]:
                j += 1
            pi[i] = j

            if pi[i] == m:
                count += 1

        return count
        
    def _KMP_match(self, text:str, query: List[str]) -> Dict:
        result = []
        for i in query:
            result.append(self._KMP_match_1_query(text, i))

        total_queries = len(self.queries)

        return {
            'total_queries': total_queries,
            'query': query,
            'matched_queries': result,
            'method_used': "KMP",
        }
    
    def _BM_match_1_query(self, text:str, query: str) -> List:
        """ Boyer-Moore algorithm to find all occurrences of a query in the extracted text """
        """ source : https://cp-algorithms.com/string/boyer-moore.html """

        s = query
        t = text
        m = len(s)
        n = len(t)

        if m == 0:
            return []

        last = {}
        for i in range(m):
            last[s[i]] = i

        j = 0
        count = 0
        positions = []

        while j <= n - m:
            i = m - 1
            while i >= 0 and s[i] == t[j + i]:
                i -= 1
            if i < 0:
                count += 1
                positions.append(j)
                j += (m - last.get(t[j + m], -1)) if j + m < n else 1
            else:
                j += max(1, i - last.get(t[j + i], -1))

        return count

    def _BM_match(self, text:str, query: List[str]) -> Dict:
        result = []
        for i in query:
            result.append(self._BM_match_1_query(text, i))

        total_queries = len(self.queries)

        return {
            'total_queries': total_queries,
            'query': query,
            'matched_queries': result,
            'method_used': "BM",
        }

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance"""
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        # Simple similarity calculation
        longer = str1 if len(str1) > len(str2) else str2
        shorter = str2 if len(str1) > len(str2) else str1
        
        if len(longer) == 0:
            return 1.0
        
        return (len(longer) - self._levenshtein_distance(longer, shorter)) / len(longer)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        dp = list(range(len(s2) + 1))
        for i in range(1, len(s1) + 1):
            new_dp = [i] * (len(s2) + 1)
            for j in range(1, len(s2) + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                new_dp[j] = min(dp[j] + 1, new_dp[j - 1] + 1, dp[j - 1] + cost)
            dp = new_dp

        return dp[len(s2)]
    
    def _fuzzy_match_1_query(self, text:str, query: str, threshold:float) -> Dict:
        assert threshold >= 0 and threshold <= 1, "Threshold must be between 0 and 1"

        """Fuzzy matching using simple similarity calculation"""

        matches = []
        count = 0
        
        for word in text.split():
            if (query in word.lower()):
                matches.append(word)
                count += 1
                continue

            if (len(query)*2 < len(word) or len(word)*2 < len(query)):
                continue

            if self._calculate_similarity(word, query) > threshold:
                matches.append(word)
                count += 1

        return count
    
    def _fuzzy_match(self, text:str, query: List[str], threshold: float = 0.8) -> Dict:
        result = []
        for i in query:
            result.append(self._fuzzy_match_1_query(text, i, threshold))

        total_queries = len(self.queries)

        return {
            'total_queries': total_queries,
            'query': query,
            'matched_queries': result,
            'method_used': "fuzzy",
        }

if __name__ == "__main__":
    matcher = Matcher(["10554236.pdf"], ["financial", "other"])
    print(matcher.match("KMP"))
    print(matcher.match("BM"))
    print(matcher.match("exact"))
    print(matcher.match("fuzzy", threshold=0.6))
    print(matcher.match("AC"))