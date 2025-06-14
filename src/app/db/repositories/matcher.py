import os
import re
from collections import Counter, deque
from typing import List, Dict, Tuple, Union
import fitz

class Matcher:
    def __init__(self, cv_paths: List[str], queries: List[str]):
        self.cv_paths = cv_paths
        self.texts = []

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
                print("Aho-Corasick algorithm is not implemented yet.")
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
        text
        
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
    matcher = Matcher(["10554236.pdf"], ["financel"])
    print(matcher.match("KMP"))
    print(matcher.match("BM"))
    print(matcher.match("exact"))
    print(matcher.match("fuzzy", threshold=0.6))