from typing import Dict, Any, Optional, List, TYPE_CHECKING
import logging

from vschart.constants import Color
from vschart.series_primitive import SeriesPrimitive
from vschart.types import TimeType

if TYPE_CHECKING:
    from vschart.series_base import SeriesBase

class VolumeProfile(SeriesPrimitive):
    """Volume Profile Plugin"""
    
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__(series, id)
        
    def set_fill_color(self, fill_color: str = Color.VOLUME_BLUE_FILL):
        """Set fill color"""
        result = self.send_request('applyOptions', [self.id, {'fillColor': fill_color}])
        if result['success']:
            self.logger.debug(f"Fill color set to {fill_color}")
        else:
            self.logger.error(f"Failed to set fill color to {fill_color}")
        
    def set_bar_color(self, bar_color: str = Color.VOLUME_BLUE_BAR):
        """Set bar color"""
        result = self.send_request('applyOptions', [self.id, {'barColor': bar_color}])
        if result['success']:
            self.logger.debug(f"Bar color set to {bar_color}")
        else:
            self.logger.error(f"Failed to set bar color to {bar_color}")
    
    def set_background_color(self, background_color: str = 'rgba(200, 200, 200, 0.1)'):
        """Set background color"""
        result = self.send_request('applyOptions', [self.id, {'backgroundColor': background_color}])
        if result['success']:
            self.logger.debug(f"Background color set to {background_color}")
        else:
            self.logger.error(f"Failed to set background color to {background_color}")
    
    def set_border_color(self, border_color: str = 'rgba(100, 100, 100, 0.3)'):
        """Set border color"""
        result = self.send_request('applyOptions', [self.id, {'borderColor': border_color}])
        if result['success']:
            self.logger.debug(f"Border color set to {border_color}")
        else:
            self.logger.error(f"Failed to set border color to {border_color}")
    
    def set_border_width(self, border_width: int = 1):
        """Set border width"""
        result = self.send_request('applyOptions', [self.id, {'borderWidth': border_width}])
        if result['success']:
            self.logger.debug(f"Border width set to {border_width}")
        else:
            self.logger.error(f"Failed to set border width to {border_width}")
    
    def set_number_of_bins(self, number_of_bins: int = 20):
        """Set number of bins for the histogram"""
        result = self.send_request('applyOptions', [self.id, {'numberOfBins': number_of_bins}])
        if result['success']:
            self.logger.debug(f"Number of bins set to {number_of_bins}")
        else:
            self.logger.error(f"Failed to set number of bins to {number_of_bins}")
        
    def set_opacity(self, opacity: float = 0.8):
        """Set opacity"""
        result = self.send_request('applyOptions', [self.id, {'opacity': opacity}])
        if result['success']:
            self.logger.debug(f"Opacity set to {opacity}")
        else:
            self.logger.error(f"Failed to set opacity to {opacity}")

    def set_width_percentage(self, width_percentage: int = 50):
        """Set the percentage of total width to use for histogram bars

        Args:
            width_percentage: Percentage of total width (0-100)
        """
        if not 0 <= width_percentage <= 100:
            self.logger.warning(f"Width percentage {width_percentage} out of range (0-100), clamping to valid range")
            width_percentage = max(0, min(100, width_percentage))
        result = self.send_request('applyOptions', [self.id, {'widthPercentage': width_percentage}])
        if result['success']:
            self.logger.debug(f"Width percentage set to {width_percentage}%")
        else:
            self.logger.error(f"Failed to set width percentage to {width_percentage}%")
