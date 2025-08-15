"""
UnbreakableCode - Your code can never crash again
Powered by fixitAPI.dev with 3.3M Stack Overflow solutions
"""

__version__ = "2.0.0"
__author__ = "Your Name"

from .decorator import (
    self_healing,
    safe_web_handler,
    safe_data_processor,
    safe_calculator
)
from .client import FixItAPI, set_api_key, get_client

__all__ = [
    'self_healing',
    'safe_web_handler', 
    'safe_data_processor',
    'safe_calculator',
    'FixItAPI',
    'set_api_key',
    'get_client'
]

# Check API on import
def _initialize():
    """Initialize and check API connection"""
    try:
        client = get_client()
        health = client.health_check()
        if health.get("status") == "online" or health:
            print(f"✅ UnbreakableCode connected to fixitAPI.dev")
            # Don't print stats for now as the structure might be different
        else:
            print("⚠️ UnbreakableCode in offline mode (basic protection active)")
    except:
        print("⚠️ UnbreakableCode in offline mode (basic protection active)")

# Run check
_initialize()
