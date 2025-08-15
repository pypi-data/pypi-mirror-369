from typing import List, Dict, Union, Any, TYPE_CHECKING

from vschart.series_primitive import SeriesPrimitive
from vschart.types import TimeType
from vschart.constants import Color

if TYPE_CHECKING:
    from vschart.series_base import SeriesBase

class BackgroundColor(SeriesPrimitive):
    """Background Color Plugin"""
    
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__(series, id)
        
    def set_color(self, color: str = Color.TRANS_BLUE):
        """Set background color"""
        result = self.send_request('applyOptions', [self.id, {'color': color}])
        if result['success']:
            self.logger.debug(f"Background color set to {color}")
        else:
            self.logger.error(f"Failed to set background color to {color}")
        
    def set_opacity(self, opacity: float = 0.5):
        """Set background opacity"""
        result = self.send_request('applyOptions', [self.id, {'opacity': opacity}])
        if result['success']:
            self.logger.debug(f"Background opacity set to {opacity}")
        else:
            self.logger.error(f"Failed to set background opacity to {opacity}")
    