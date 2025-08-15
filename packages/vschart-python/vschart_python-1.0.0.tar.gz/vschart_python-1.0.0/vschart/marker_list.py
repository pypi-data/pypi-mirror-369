from datetime import datetime
from typing import List, Dict, Any, Union
import pandas as pd

from vschart.base import Base
from vschart.constants import MarkerPosition, MarkerShape, Color
from vschart.types import TimeType, to_timestamp


class MarkerList(Base):
    def __init__(self):
        super().__init__()
        self.list: List[Dict[str, Any]] = []
        
    def add_marker(self, time: TimeType, position: str = MarkerPosition.BELOW_BAR, shape: str = MarkerShape.ARROW_UP, color: int = Color.RED, size: int = 1, text: str = ''):
        marker = {
            "time": time,
            "position": position,
            "shape": shape,
            "color": color,
            "size": size,
            "text": text
        }
        self.list.append(marker)
        
    def time_key(self, time_value: TimeType) -> float:
        """Convert various time formats to a comparable float timestamp."""
        try:
            return to_timestamp(time_value)
        except:
            return float('inf')  # Put invalid values at the end
    
    def sort(self):
        """Sort markers by time using a robust comparison method."""
        self.list.sort(key=lambda x: self.time_key(x["time"]))
        
    def clear(self):
        """Clear all markers from the list."""
        self.list = []