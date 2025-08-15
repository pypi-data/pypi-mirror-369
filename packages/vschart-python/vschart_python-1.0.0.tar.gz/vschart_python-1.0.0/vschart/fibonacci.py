from typing import Dict, Any, Optional, List, TYPE_CHECKING
import logging

from vschart.constants import Color
from vschart.series_primitive import SeriesPrimitive
from vschart.types import TimeType

if TYPE_CHECKING:
    from vschart.series_base import SeriesBase

class Fibonacci(SeriesPrimitive):
    """Fibonacci Retracement Plugin"""
    
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__(series, id)
        
    def send_request(self, method: str, params: List[Any] = None) -> Any:
        """Send request to the chart"""
        result = self.series.send_request(method, params)
        return result
        
    def set_trend_line_color(self, trend_line_color: str = Color.BLACK):
        """Set trend line color"""
        result = self.send_request('applyOptions', [self.id, {'trendLineColor': trend_line_color}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Trend line color set to {trend_line_color}")
        else:
            self.logger.error(f"Failed to set trend line color to {trend_line_color}")
        
    def set_trend_line_width(self, trend_line_width: int = 2):
        """Set trend line width"""
        result = self.send_request('applyOptions', [self.id, {'trendLineWidth': trend_line_width}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Trend line width set to {trend_line_width}")
        else:
            self.logger.error(f"Failed to set trend line width to {trend_line_width}")
        
    def set_fib_colors(self, fib_colors: List[str] = None):
        """Set fibonacci line colors"""
        if fib_colors is None:
            fib_colors = [
                Color.RED,        # 0%
                Color.ORANGE,     # 38.2%
                Color.YELLOW,     # 61.8%
                Color.GREEN,      # 100%
                Color.BLUE        # 161.8%
            ]
        result = self.send_request('applyOptions', [self.id, {'fibColors': fib_colors}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Fibonacci line colors set to {fib_colors}")
        else:
            self.logger.error(f"Failed to set fibonacci line colors to {fib_colors}")
        
    def set_fib_line_width(self, fib_line_width: int = 1):
        """Set fibonacci line width"""
        result = self.send_request('applyOptions', [self.id, {'fibLineWidth': fib_line_width}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Fibonacci line width set to {fib_line_width}")
        else:
            self.logger.error(f"Failed to set fibonacci line width to {fib_line_width}")
        
    def set_coefficients(self, coefficients: List[float] = None):
        """Set fibonacci coefficients"""
        if coefficients is None:
            coefficients = [0, 0.382, 0.618, 1, 1.618]
        result = self.send_request('applyOptions', [self.id, {'coefficients': coefficients}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Fibonacci coefficients set to {coefficients}")
        else:
            self.logger.error(f"Failed to set fibonacci coefficients to {coefficients}")
        
    def set_extension_bars(self, extension_bars: int = -1):
        """Set extension bars"""
        result = self.send_request('applyOptions', [self.id, {'extensionBars': extension_bars}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Extension bars set to {extension_bars}")
        else:
            self.logger.error(f"Failed to set extension bars to {extension_bars}")
        
    def set_show_labels(self, show_labels: bool = True):
        """Set show labels"""
        result = self.send_request('applyOptions', [self.id, {'showLabels': show_labels}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Show labels set to {show_labels}")
        else:
            self.logger.error(f"Failed to set show labels to {show_labels}")
        
    def set_label_background_color(self, label_background_color: str = Color.WHITE):
        """Set label background color"""
        result = self.send_request('applyOptions', [self.id, {'labelBackgroundColor': label_background_color}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Label background color set to {label_background_color}")
        else:
            self.logger.error(f"Failed to set label background color to {label_background_color}")
        
    def set_label_text_color(self, label_text_color: str = Color.BLACK):
        """Set label text color"""
        result = self.send_request('applyOptions', [self.id, {'labelTextColor': label_text_color}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Label text color set to {label_text_color}")
        else:
            self.logger.error(f"Failed to set label text color to {label_text_color}")
    
    def set_fill_colors(self, fill_colors: List[str] = None):
        """Set fibonacci fill colors"""
        if fill_colors is None:
            fill_colors = [
                'rgba(255, 0, 0, 0.1)',     # Light red fill
                'rgba(255, 165, 0, 0.1)',   # Light orange fill
                'rgba(255, 255, 0, 0.1)',   # Light yellow fill
                'rgba(0, 255, 0, 0.1)',     # Light green fill
                'rgba(0, 0, 255, 0.1)'      # Light blue fill
            ]
        result = self.send_request('applyOptions', [self.id, {'fillColors': fill_colors}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Fill colors set to {fill_colors}")
        else:
            self.logger.error(f"Failed to set fill colors to {fill_colors}")
    
    def set_show_fill(self, show_fill: bool = True):
        """Set show fill"""
        result = self.send_request('applyOptions', [self.id, {'showFill': show_fill}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Show fill set to {show_fill}")
        else:
            self.logger.error(f"Failed to set show fill to {show_fill}")
    
    def set_fill_opacity(self, fill_opacity: float = 0.1):
        """Set fill opacity"""
        result = self.send_request('applyOptions', [self.id, {'fillOpacity': fill_opacity}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Fill opacity set to {fill_opacity}")
        else:
            self.logger.error(f"Failed to set fill opacity to {fill_opacity}")
    
    def set_label_font_size(self, label_font_size: int = 12):
        """Set label font size"""
        result = self.send_request('applyOptions', [self.id, {'labelFontSize': label_font_size}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Label font size set to {label_font_size}")
        else:
            self.logger.error(f"Failed to set label font size to {label_font_size}")
    
    def set_label_position(self, label_position: str = 'left'):
        """Set label position ('left' or 'right')"""
        result = self.send_request('applyOptions', [self.id, {'labelPosition': label_position}])
        if result and isinstance(result, dict) and result.get('success'):
            self.logger.debug(f"Label position set to {label_position}")
        else:
            self.logger.error(f"Failed to set label position to {label_position}")
