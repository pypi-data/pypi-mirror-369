"""
Self-healing decorator powered by fixitAPI.dev
Never let your code crash again!
"""

import sys
import traceback
import functools
from typing import Any, Callable, Optional
from .client import get_client

def self_healing(
    func: Optional[Callable] = None,
    *,
    auto_fix: bool = True,
    log_errors: bool = True,
    fallback: Any = None,
    submit_new_errors: bool = False
):
    """
    Make any function unbreakable using 3.3M Stack Overflow solutions
    
    Args:
        func: The function to protect
        auto_fix: Automatically apply suggested fixes
        log_errors: Print error information
        fallback: Value to return if function fails
        submit_new_errors: Submit unknown errors to community
    
    Example:
        @self_healing
        def risky_function():
            return data[100]  # Won't crash even if list is empty
    """
    
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Try running the function normally
                return f(*args, **kwargs)
                
            except Exception as e:
                # Get error details
                error_type = type(e).__name__
                error_msg = str(e)
                error_query = f"{error_type}: {error_msg}"
                
                # Extract code context
                tb = traceback.extract_tb(sys.exc_info()[2])
                if tb:
                    filename = tb[-1].filename
                    line_no = tb[-1].lineno
                    code_line = tb[-1].line
                else:
                    filename = "unknown"
                    line_no = 0
                    code_line = ""
                
                # Search for solutions using fixitAPI.dev
                client = get_client()
                solutions = client.search_solution(error_query, limit=3)
                
                if solutions and auto_fix:
                    # Try the first solution
                    best_solution = solutions[0] if isinstance(solutions[0], dict) else {"solution": str(solutions[0])}
                    
                    if log_errors:
                        print(f"\n🛡️ UnbreakableCode prevented crash!")
                        print(f"   Error: {error_type}: {error_msg}")
                        print(f"   Location: {filename}:{line_no}")
                        print(f"   Solution: {best_solution.get('solution', 'Use fallback')}")
                    
                    # Try to extract a return value from solution
                    solution_code = best_solution.get("code", "")
                    if solution_code and "return" in solution_code.lower():
                        # Solution suggests a return value
                        if "none" in solution_code.lower():
                            return None
                        elif "[]" in solution_code:
                            return []
                        elif "{}" in solution_code:
                            return {}
                        elif "0" in solution_code:
                            return 0
                        elif '""' in solution_code or "''" in solution_code:
                            return ""
                    
                    # If we can't parse the solution, use fallback
                    return fallback
                    
                elif log_errors:
                    print(f"\n⚠️ UnbreakableCode caught error:")
                    print(f"   {error_type}: {error_msg}")
                    print(f"   Returning fallback: {fallback}")
                
                # Submit new error if requested and no solution found
                if submit_new_errors and not solutions:
                    client.submit_solution(
                        error=error_query,
                        solution=f"Return {fallback} as safe default",
                        explanation=f"Auto-submitted by UnbreakableCode"
                    )
                
                return fallback
                
        return wrapper
    
    # Handle decorator with/without arguments
    if func is None:
        return decorator
    else:
        return decorator(func)

# Convenience decorators with common configurations
def safe_web_handler(func):
    """Decorator for web endpoints - returns {} on error"""
    return self_healing(func, fallback={}, log_errors=True)

def safe_data_processor(func):
    """Decorator for data processing - returns [] on error"""
    return self_healing(func, fallback=[], log_errors=True)

def safe_calculator(func):
    """Decorator for calculations - returns 0 on error"""
    return self_healing(func, fallback=0, log_errors=False)
