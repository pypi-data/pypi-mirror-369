from typing import List, Dict, Any, TYPE_CHECKING
from datetime import datetime

from vschart.base import Base
from vschart.constants import MarkerPosition, MarkerShape, Color

if TYPE_CHECKING:
    from vschart.series_base import SeriesBase

class SeriesMarkers(Base):
    
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__()
        self.series = series
        self.id = id
        
    def send_request(self, method: str, params: List[Any] = None) -> Any:
        """Send request to the chart"""
        return self.series.send_request(method, params)
        
    def delete(self):
        self.send_request('removeSeriesMarkers', [self.id])
