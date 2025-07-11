import os
import re
from typing import List, Dict, Union, Tuple
import fitz
import time
import copy
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, as_completed

def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

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


def calculate_similarity(str1: str, str2: str) -> float:
    if len(str1) == 0 or len(str2) == 0:
        return 0.0
    longer = str1 if len(str1) > len(str2) else str2
    shorter = str2 if len(str1) > len(str2) else str1
    if len(longer) == 0:
        return 1.0
    return (len(longer) - levenshtein_distance(longer, shorter)) / len(longer)


def fuzzy_match_1_query(text: str, query: str, threshold: float) -> int:
    assert 0 <= threshold <= 1, "Threshold must be between 0 and 1"
    count = 0
    for word in text.split():
        if len(query) * 2 < len(word) or len(word) * 2 < len(query):
            continue
        if calculate_similarity(word, query) > threshold:
            count += 1
    return count

def fuzzy_match_worker(j, i, text, query, threshold):
    count = fuzzy_match_1_query(text, query, threshold)
    return (j, i, count)

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
                else:
                    ch = 36


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
        sum = 0

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
                    sum += 1

        # Return the final result dictionary
        return {
            'keywords' : self.words,
            'matched_queries': results,
            'total_matched': sum
        }

class Matcher:
    def __init__(self, sources: List[Tuple[str, str]], queries: List[str]):
        self.sources_id = [source[0] for source in sources]
        self.cv_paths = [source[1] for source in sources]
        self.automaton_trie = None

        self.queries = [query.lower() for query in queries]
        self.texts = self._extract_texts_concurrently()

        self.exact_match_calculation_time = 0
        self.fuzzy_match_calculation_time = 0

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
            print(f"Finished extracting text from {path}")
            return result
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def _extract_texts_concurrently(self) -> List[str]:
        def worker(path: str) -> str:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
            return self.extract_text(path, 0)

        results = [None] * len(self.cv_paths)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(worker, path): i for i, path in enumerate(self.cv_paths)}
            
            for future in concurrent.futures.as_completed(futures):
                i = futures[future]
                try:
                    results[i] = future.result()
                except Exception as e:
                    print(f"[Error] Failed to extract from {self.cv_paths[i]}: {e}")
                    results[i] = ""

        return results
    
    def set_keywords(self, queries: List[str]):
        """Set the keywords for matching + restart all calculations"""
        if not queries:
            raise ValueError("Queries list cannot be empty")
        self.queries = [query.lower() for query in queries]
        self.automaton_trie = AhoCorasick(self.queries)
        self.exact_match_calculation_time = 0
        self.fuzzy_match_calculation_time = 0

    def _extract_from_pdf(self, path: str) -> str:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    
    def match(self, method: str, threshold: float = 0.7) -> Dict:
        if not self.queries:
            raise ValueError("Queries list is empty")


        result = []    
        counter = [0] * len(self.queries)  # Counter for each query

        # exact matching
        for i in range(len(self.sources_id)):
            text = self.texts[i]
            id = self.sources_id[i]

            time_start = time.time()

            if method == 'exact':
                result.append({
                    "id" : id,
                    "result" : self._exact_match(text, self.queries)
                    })
            elif method == 'KMP':
                result.append({
                    "id" : id,
                    "result" : self._exact_match(text, self.queries)
                    })
            elif method == 'BM':
                result.append({
                    "id" : id,
                    "result" : self._exact_match(text, self.queries)
                    })
            elif method == 'AC':
                automaton_trie = AhoCorasick(self.queries)
                result.append({
                    "id" : id,
                    "result" : automaton_trie.search_words(text)
                })
            elif method == 'fuzzy':
                result.append({
                    "id" : id,
                    "result" : self._fuzzy_match(text, self.queries, threshold)
                })
            else:
                raise ValueError(f"Unsupported matching method: {method}")

            time_end = time.time()
            self.exact_match_calculation_time += (time_end - time_start)

            for j in range(len(self.queries)):
                counter[j] += result[i]['result']['matched_queries'][j]

        # fuzzy matching
        futures = []
        total_fuzzy_time = 0.0
        time_start = time.time()

        with ProcessPoolExecutor() as executor:
            for i in range(len(self.queries)):
                if counter[i] == 0:
                    for j in range(len(self.sources_id)):
                        futures.append(executor.submit(
                            fuzzy_match_worker,
                            j,
                            i,
                            self.texts[j],
                            self.queries[i],
                            threshold
                        ))

            for future in as_completed(futures):
                j, i, count = future.result()
                result[j]['result']['matched_queries'][i] = count
                result[j]['result']['total_matched'] += count

        self.fuzzy_match_calculation_time = time.time() - time_start

        return result, self.exact_match_calculation_time, self.fuzzy_match_calculation_time

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
        result_sum = 0
        for query in queries:
            result = self._exact_match_1_query(text, query)
            results.append(result)
            result_sum += result

        return {
            'keywords' : queries,
            'matched_queries': results,
            'total_matched': result_sum
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
        
    def _KMP_match(self, text:str, queries: List[str]) -> Dict:
        results = []
        result_sum = 0
        for i in queries:
            results.append(self._KMP_match_1_query(text, i))
            result_sum += results[-1]

        return {
            'keywords' : queries,
            'matched_queries': results,
            'total_matched': result_sum
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

    def _BM_match(self, text:str, queries: List[str]) -> Dict:
        results = []
        result_sum = 0
        for i in queries:
            results.append(self._BM_match_1_query(text, i))
            result_sum += results[-1]

        return {
            'keywords' : queries,
            'matched_queries': results,
            'total_matched': result_sum,
        }
    
    def get_skills(self, cv_path: str) -> List[str]:
        """ Extract skills from CV """
        # TODO

        # format : [skill1, skill2, ...]
        print("test")
        return []
    
    def get_summaries(self, cv_path: str) -> List[str]:
        """ Extract summary information from CV """
        cv_text = self.read_pdf(cv_path)
        if not cv_text:
            return []
        
        summary_text = self.extract_section(cv_text, self.summary_patterns)
        
        if summary_text:
            return [summary_text]
        else:
            return []
    
    def get_job_histories(self, cv_path: str) -> List[str]:
        """ Extract experience information from CV """
        # TODO

        # format : [{position, company, period}]
        print("test")
        return []
    
    def get_educations(self, cv_path: str) -> List[str]:
        """ Extract education information from CV """
        # TODO
        # format : [{degree, institution, period}]
        print("test")
        return []


if __name__ == "__main__":
    matcher = Matcher(["10554236.pdf"], ["financial", "other"])
    print(matcher.match("KMP"))
    print(matcher.match("BM"))
    print(matcher.match("exact"))
    print(matcher.match("fuzzy", threshold=0.7))
    print(matcher.match("AC"))