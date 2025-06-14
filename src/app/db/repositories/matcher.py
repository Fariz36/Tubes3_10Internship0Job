import os
import re
from collections import Counter
from typing import List, Dict, Tuple, Union
import fitz

class Matcher:
    def __init__(self, cv_path: str, queries: List[str], method: str = 'exact'):
        self.path = cv_path
        self.queries = queries

        # Extract text in both cases
        self.extracted_string_lower_case = self.extract_text(cv_path, case=0)
        self.extracted_string_original = self.extract_text(cv_path, case=1)

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

    def _extract_from_pdf(self, path: str) -> str:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _exact_match(self, query: str) -> Dict:
        query_lower = query.lower()
        text_lower = self.extracted_string_lower_case
        
        matches = []
        count = 0
        start = 0
        
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            matches.append(pos)
            count += 1
            start = pos + 1
        
        return {
            'query': query,
            'count': count,
            'positions': matches,
            'found': count > 0,
            'method': 'exact'
        }
    
    def _KMP_match_1_query(self, query: str) -> List:
        """ KMP algorithm to find all occurrences of a query in the extracted text """
        """ source : https://cp-algorithms.com/string/prefix-function.html """

        s =  query.lower() + "#" + self.extracted_string_lower_case
        n = len(self.extracted_string_lower_case)
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
        
    def _KMP_match(self, query: str) -> Dict:
        result = []
        for i in query:
            result.append(self._KMP_match_1_query(i))

        total_queries = len(self.queries)

        return {
            'total_queries': total_queries,
            'query': query,
            'matched_queries': result,
            'method_used': "KMP",
            'cv_file': os.path.basename(self.path)
        }
    
    def _BM_match_1_query(self, query: str) -> List:
        """ Boyer-Moore algorithm to find all occurrences of a query in the extracted text """
        """ source : https://cp-algorithms.com/string/boyer-moore.html """

        s = query.lower()
        t = self.extracted_string_lower_case
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

    def _BM_match(self, query: str) -> Dict:
        result = []
        for i in query:
            result.append(self._BM_match_1_query(i))

        total_queries = len(self.queries)

        return {
            'total_queries': total_queries,
            'query': query,
            'matched_queries': result,
            'method_used': "BM",
            'cv_file': os.path.basename(self.path)
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
    
    def _fuzzy_match_1_query(self, query: str, threshold:float) -> Dict:
        assert threshold >= 0 and threshold <= 1, "Threshold must be between 0 and 1"

        """Fuzzy matching using simple similarity calculation"""
        query_lower = query.lower()
        text_lower = self.extracted_string_lower_case
        
        matches = []
        count = 0
        
        for word in text_lower.split():
            if (query_lower in word.lower()):
                matches.append(word)
                count += 1
                continue

            if (len(query_lower)*2 < len(word) or len(word)*2 < len(query_lower)):
                continue

            if self._calculate_similarity(word, query_lower) > threshold:
                matches.append(word)
                count += 1

        return count
    
    def _fuzzy_match(self, query: str, threshold: float = 0.8) -> Dict:
        result = []
        for i in query:
            result.append(self._fuzzy_match_1_query(i, threshold))

        total_queries = len(self.queries)

        return {
            'total_queries': total_queries,
            'query': query,
            'matched_queries': result,
            'method_used': "fuzzy",
            'cv_file': os.path.basename(self.path)
        }

if __name__ == "__main__":
    file_path = "10554236.pdf"
    matcher = Matcher(file_path, ["Financial"])
    print(matcher.extracted_string_lower_case)
    print(matcher._KMP_match(["other"]))

    print(matcher._fuzzy_match(["respond", "Financal"], threshold=0.6))