"""Type definitions for VSChart Python library."""

from typing import Union
from datetime import datetime
import pandas as pd

# TIME type union for flexible time representation
TimeType = Union[datetime, pd.Timestamp, str, int, float]

def to_timestamp(time: TimeType) -> float:
    """Convert various time formats to float timestamp.
    
    Args:
        time: Input time in various formats (datetime, Timestamp, str, int, float)
        
    Returns:
        float: Unix timestamp as float
        
    Raises:
        ValueError: If time format is not supported
    """
    if isinstance(time, pd.Timestamp):
        return time.timestamp()
    elif isinstance(time, datetime):
        return time.timestamp()
    elif isinstance(time, str):
        return pd.Timestamp(time).timestamp()
    elif isinstance(time, (int, float)):
        return float(time)
    else:
        raise ValueError(f"Unsupported time format: {type(time)}")
