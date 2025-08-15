from typing import List, Any
from vschart.base import Base

class SeriesPrimitive(Base):
    """Base class for series primitives"""
    
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__()
        self.series = series
        self.id = id

    def send_request(self, method: str, params: List[Any] = None) -> Any:
        """Send request to the chart"""
        return self.series.send_request(method, params)
        
    def delete(self):
        self.series.remove_primitive(self.id)

