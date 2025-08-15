"""Tooltip implementation for VSChart Python package.

This module provides the Tooltip class for adding interactive tooltips
to chart series that display price and time information on hover.
Tooltips can be customized with various styling options including colors,
font properties, and positioning.
"""

from vschart.series_primitive import SeriesPrimitive
from vschart.constants import Color

class Tooltip(SeriesPrimitive):
    """
    Tooltip class for adding interactive tooltips to chart series.
    
    Tooltips display price and time information when hovering over chart data points.
    """
    
    def __init__(self, series: 'SeriesBase', id: str):
        """
        Initialize a new Tooltip instance.
        
        Args:
            series: The series to attach the tooltip to
            id: The unique identifier for this tooltip
        """
        super().__init__(series, id)
        
    def set_title(self, title: str):
        """
        Set the tooltip title.
        
        Args:
            title: The title text to display in the tooltip
        """
        result = self.send_request('applyOptions', [self.id, {'title': title}])
        if result['success']:
            self.logger.debug(f"Title set to {title}")
        else:
            self.logger.error(f"Failed to set title to {title}")
            
    def set_y_position(self, y_position: int):
        """
        Set the tooltip Y-axis position relative to the top of its containing pane.
        
        Args:
            y_position: The Y-axis position in pixels
        """
        result = self.send_request('applyOptions', [self.id, {'yPosition': y_position}])
        if result['success']:
            self.logger.debug(f"Y position set to {y_position}")
        else:
            self.logger.error(f"Failed to set Y position to {y_position}")
    
    def set_background_color(self, color: str):
        """
        Set the tooltip background color.
        
        Args:
            color: The background color for the tooltip
        """
        result = self.send_request('applyOptions', [self.id, {'backgroundColor': color}])
        if result['success']:
            self.logger.debug(f"Background color set to {color}")
        else:
            self.logger.error(f"Failed to set background color to {color}")
    
    def set_text_color(self, color: str):
        """
        Set the tooltip text color.
        
        Args:
            color: The text color for the tooltip
        """
        result = self.send_request('applyOptions', [self.id, {'textColor': color}])
        if result['success']:
            self.logger.debug(f"Text color set to {color}")
        else:
            self.logger.error(f"Failed to set text color to {color}")
    
    def set_font_size(self, size: int):
        """
        Set the tooltip font size.
        
        Args:
            size: The font size in pixels
        """
        result = self.send_request('applyOptions', [self.id, {'fontSize': size}])
        if result['success']:
            self.logger.debug(f"Font size set to {size}")
        else:
            self.logger.error(f"Failed to set font size to {size}")
    
    def set_font_family(self, family: str):
        """
        Set the tooltip font family.
        
        Args:
            family: The font family name
        """
        result = self.send_request('applyOptions', [self.id, {'fontFamily': family}])
        if result['success']:
            self.logger.debug(f"Font family set to {family}")
        else:
            self.logger.error(f"Failed to set font family to {family}")
    
    def set_padding(self, padding: int):
        """
        Set the tooltip padding.
        
        Args:
            padding: The padding in pixels
        """
        result = self.send_request('applyOptions', [self.id, {'padding': padding}])
        if result['success']:
            self.logger.debug(f"Padding set to {padding}")
        else:
            self.logger.error(f"Failed to set padding to {padding}")