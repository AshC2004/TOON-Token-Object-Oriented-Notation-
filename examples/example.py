"""Example Python file for TOON conversion demonstration."""

from typing import List, Optional
import asyncio


class DataProcessor:
    """Processes data with various transformation methods."""

    def __init__(self, name: str):
        """Initialize processor with a name."""
        self.name = name
        self.results = []

    def process(self, data: List[int]) -> List[int]:
        """Process a list of integers."""
        results = []
        for item in data:
            if item > 0:
                results.append(item * 2)
        return results

    async def async_process(self, data: List[int]) -> List[int]:
        """Asynchronously process data."""
        await asyncio.sleep(0.1)
        return self.process(data)


def calculate_total(items: List[float]) -> float:
    """Calculate the total sum of items."""
    total = 0.0
    for item in items:
        total += item
    return total


async def fetch_data(url: str) -> Optional[dict]:
    """Fetch data from a URL."""
    try:
        # Simulate API call
        await asyncio.sleep(1)
        return {"status": "success", "data": [1, 2, 3]}
    except Exception as e:
        print(f"Error: {e}")
        return None


MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
