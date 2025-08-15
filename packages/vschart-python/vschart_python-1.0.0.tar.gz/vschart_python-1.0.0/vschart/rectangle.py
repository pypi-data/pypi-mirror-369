from typing import Dict, Any, Optional, List, TYPE_CHECKING
import logging

from vschart.constants import Color
from vschart.series_primitive import SeriesPrimitive
from vschart.types import TimeType

if TYPE_CHECKING:
    from vschart.series_base import SeriesBase

class Rectangle(SeriesPrimitive):
    """Rectangle Plugin"""
    
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__(series, id)
        
    def set_border_color(self, border_color: str = Color.BLACK):
        """Set border color"""
        result = self.send_request('applyOptions', [self.id, {'borderColor': border_color}])
        if result['success']:
            self.logger.debug(f"Border color set to {border_color}")
        else:
            self.logger.error(f"Failed to set border color to {border_color}")
        
    def set_border_width(self, border_width: int = 2):
        """Set border width"""
        result = self.send_request('applyOptions', [self.id, {'borderWidth': border_width}])
        if result['success']:
            self.logger.debug(f"Border width set to {border_width}")
        else:
            self.logger.error(f"Failed to set border width to {border_width}")
        
    def set_line_style(self, line_style: str = 'solid'):
        """Set line style"""
        result = self.send_request('applyOptions', [self.id, {'lineStyle': line_style}])
        if result['success']:
            self.logger.debug(f"Line style set to {line_style}")
        else:
            self.logger.error(f"Failed to set line style to {line_style}")
        
    def set_fill_color(self, fill_color: str = Color.TRANS_BLUE):
        """Set fill color"""
        result = self.send_request('applyOptions', [self.id, {'fillColor': fill_color}])
        if result['success']:
            self.logger.debug(f"Fill color set to {fill_color}")
        else:
            self.logger.error(f"Failed to set fill color to {fill_color}")
        
    def set_show_text(self, show_text: bool = True):
        """Set show text"""
        result = self.send_request('applyOptions', [self.id, {'showText': show_text}])
        if result['success']:
            self.logger.debug(f"Show text set to {show_text}")
        else:
            self.logger.error(f"Failed to set show text to {show_text}")
        
    def set_text_position(self, text_position: str = 'inside'):
        """Set text position"""
        result = self.send_request('applyOptions', [self.id, {'textPosition': text_position}])
        if result['success']:
            self.logger.debug(f"Text position set to {text_position}")
        else:
            self.logger.error(f"Failed to set text position to {text_position}")
        
    def set_text_color(self, text_color: str = Color.BLACK):
        """Set text color"""
        result = self.send_request('applyOptions', [self.id, {'textColor': text_color}])
        if result['success']:
            self.logger.debug(f"Text color set to {text_color}")
        else:
            self.logger.error(f"Failed to set text color to {text_color}")
        
    def set_text_background_color(self, text_background_color: str = Color.TRANS_WHITE):
        """Set text background color"""
        result = self.send_request('applyOptions', [self.id, {'textColor': text_color}])
        if result['success']:
            self.logger.debug(f"Text background color set to {text_background_color}")
        else:
            self.logger.error(f"Failed to set text background color to {text_background_color}")
        
    def set_text_size(self, text_size: int = 12):
        """Set text size"""
        result = self.send_request('applyOptions', [self.id, {'textSize': text_size}])
        if result['success']:
            self.logger.debug(f"Text size set to {text_size}")
        else:
            self.logger.error(f"Failed to set text size to {text_size}")
        
    def set_text_font(self, text_font: str = 'Arial'):
        """Set text font"""
        result = self.send_request('applyOptions', [self.id, {'textFont': text_font}])
        if result['success']:
            self.logger.debug(f"Text font set to {text_font}")
        else:
            self.logger.error(f"Failed to set text font to {text_font}")
