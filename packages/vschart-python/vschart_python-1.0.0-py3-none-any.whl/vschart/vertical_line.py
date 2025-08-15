from typing import List, Any, TYPE_CHECKING
from vschart.types import TimeType
from vschart.series_primitive import SeriesPrimitive
from vschart.constants import Color

if TYPE_CHECKING:
    from vschart.series_base import SeriesBase

class VerticalLine(SeriesPrimitive):
    """Vertical Line Plugin"""
    
    def __init__(self, series: 'SeriesBase', line_id: str):
        super().__init__(series, line_id)
        
    def set_color(self, color: str = Color.GREEN):
        """Set line color"""
        result = self.send_request('applyOptions', [self.id, {'color': color}])
        if result['success']:
            self.logger.debug(f"Line color set to {color}")
        else:
            self.logger.error(f"Failed to set line color to {color}")
        
    def set_label_text(self, label_text: str = ''):
        """Set label text"""
        result = self.send_request('applyOptions', [self.id, {'labelText': label_text}])
        if result['success']:
            self.logger.debug(f"Label text set to {label_text}")
        else:
            self.logger.error(f"Failed to set label text to {label_text}")
        
    def set_width(self, width: int = 3):
        """Set line width"""
        result = self.send_request('applyOptions', [self.id, {'width': width}])
        if result['success']:
            self.logger.debug(f"Line width set to {width}")
        else:
            self.logger.error(f"Failed to set line width to {width}")
        
    def set_label_background_color(self, label_background_color: str = Color.GREEN):
        """Set label background color"""
        result = self.send_request('applyOptions', [self.id, {'labelBackgroundColor': label_background_color}])
        if result['success']:
            self.logger.debug(f"Label background color set to {label_background_color}")
        else:
            self.logger.error(f"Failed to set label background color to {label_background_color}")
        
    def set_label_text_color(self, label_text_color: str = Color.WHITE):
        """Set label text color"""
        result = self.send_request('applyOptions', [self.id, {'labelTextColor': label_text_color}])
        if result['success']:
            self.logger.debug(f"Label text color set to {label_text_color}")
        else:
            self.logger.error(f"Failed to set label text color to {label_text_color}")
        
    def set_show_label(self, show_label: bool = False):
        """Set show label"""
        result = self.send_request('applyOptions', [self.id, {'showLabel': show_label}])
        if result['success']:
            self.logger.debug(f"Show label set to {show_label}")
        else:
            self.logger.error(f"Failed to set show label to {show_label}")