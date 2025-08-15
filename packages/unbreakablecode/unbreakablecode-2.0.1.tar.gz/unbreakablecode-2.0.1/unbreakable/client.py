"""
UnbreakableCode - Powered by fixitAPI.dev
3.3M Stack Overflow solutions at your fingertips
"""

import requests
import json
import os
import hashlib
from functools import lru_cache
from typing import Dict, List, Optional, Any

class FixItAPI:
    """Client for fixitAPI.dev - 3.3M Stack Overflow solutions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "http://64.23.180.90"  # Your actual server
        self.api_key = api_key or os.environ.get("FIXIT_API_KEY", "free_tier")
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })
        self._cache = {}
        self._search_method = None  # Will auto-detect
    
    def health_check(self) -> Dict[str, Any]:
        """Check API status and statistics"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=2)
            return response.json() if response.status_code == 200 else {}
        except:
            return {"status": "offline"}
    
    @lru_cache(maxsize=1000)
    def search_solution(self, error_query: str, limit: int = 5) -> List[Dict]:
        """
        Search for solutions to an error
        Auto-detects whether to use GET or POST
        
        Args:
            error_query: The error message or description
            limit: Number of results to return (default 5)
        
        Returns:
            List of solution dictionaries
        """
        # Check cache first
        cache_key = hashlib.md5(f"{error_query}:{limit}".encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Auto-detect search method if not known
        if self._search_method is None:
            self._detect_search_method()
        
        try:
            if self._search_method == "GET":
                # Use GET with query parameters
                response = self.session.get(
                    f"{self.base_url}/search",
                    params={
                        "q": error_query,
                        "query": error_query,  # Try both parameter names
                        "limit": limit
                    },
                    timeout=2
                )
            else:
                # Use POST with JSON body
                response = self.session.post(
                    f"{self.base_url}/search",
                    json={
                        "query": error_query,
                        "limit": limit
                    },
                    timeout=2
                )
            
            if response.status_code == 200:
                solutions = response.json()
                self._cache[cache_key] = solutions
                return solutions
            else:
                return self._get_offline_fallback(error_query)
                
        except Exception as e:
            # Offline fallback
            return self._get_offline_fallback(error_query)
    
    def _detect_search_method(self):
        """Auto-detect whether search endpoint uses GET or POST"""
        try:
            # Try POST first
            response = self.session.post(
                f"{self.base_url}/search",
                json={"query": "test", "limit": 1},
                timeout=1
            )
            if response.status_code != 405:
                self._search_method = "POST"
                return
            
            # Try GET
            response = self.session.get(
                f"{self.base_url}/search",
                params={"q": "test", "limit": 1},
                timeout=1
            )
            if response.status_code != 405:
                self._search_method = "GET"
                return
        except:
            pass
        
        # Default to GET if detection fails
        self._search_method = "GET"
    
    def submit_solution(self, error: str, solution: str, explanation: str = "") -> bool:
        """
        Submit a community solution
        
        Args:
            error: The error message
            solution: Your solution
            explanation: Optional explanation
        
        Returns:
            True if submitted successfully
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/community/submit",
                json={
                    "error": error,
                    "solution": solution,
                    "explanation": explanation
                },
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def vote_solution(self, submission_id: str, vote_type: str = "upvote") -> bool:
        """Vote on a community solution"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/community/vote",
                json={
                    "submission_id": submission_id,
                    "vote_type": vote_type
                },
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def _get_offline_fallback(self, error_query: str) -> List[Dict]:
        """Basic offline fallbacks for common errors"""
        error_lower = error_query.lower()
        
        if "indexerror" in error_lower or "list index" in error_lower:
            return [{
                "solution": "Check list length before accessing index",
                "code": "if index < len(items): value = items[index]",
                "confidence": 0.9
            }]
        elif "keyerror" in error_lower:
            return [{
                "solution": "Use dict.get() with default value",
                "code": "value = dict.get('key', default_value)",
                "confidence": 0.9
            }]
        elif "typeerror" in error_lower and "nonetype" in error_lower:
            return [{
                "solution": "Check for None before operations",
                "code": "if value is not None: result = value.method()",
                "confidence": 0.8
            }]
        elif "zerodivision" in error_lower:
            return [{
                "solution": "Check divisor before division",
                "code": "result = a / b if b != 0 else 0",
                "confidence": 0.95
            }]
        elif "attributeerror" in error_lower:
            return [{
                "solution": "Check attribute exists before accessing",
                "code": "if hasattr(obj, 'attribute'): obj.attribute",
                "confidence": 0.85
            }]
        elif "valueerror" in error_lower:
            return [{
                "solution": "Validate input before conversion",
                "code": "try: int(value) except ValueError: default",
                "confidence": 0.8
            }]
        else:
            return [{
                "solution": "Add error handling",
                "code": "try: risky_operation() except Exception: fallback",
                "confidence": 0.5
            }]

# Global client instance
_client = None

def get_client() -> FixItAPI:
    """Get or create the global client instance"""
    global _client
    if _client is None:
        _client = FixItAPI()
    return _client

def set_api_key(key: str):
    """Set API key for the global client"""
    client = get_client()
    client.api_key = key
    client.session.headers["X-API-Key"] = key
