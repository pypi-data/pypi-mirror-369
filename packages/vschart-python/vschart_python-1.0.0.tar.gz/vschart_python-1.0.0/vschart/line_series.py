import logging

from vschart.series_base import SeriesBase
from vschart.constants import Color, LineStyle


class LineSeries(SeriesBase):
    """Line Series"""
    
    def __init__(self, chart, id: str):
        super().__init__(chart, id)
        
    def set_color(self, color: str = Color.BRIGHT_BLUE):
        """Set color"""
        result = self.send_request('applyOptions', [self.id, {'color': color}])
        if result['success']:
            self.logger.debug(f"Color set to {color}")
        else:
            self.logger.error(f"Failed to set color to {color}")
        
    def set_line_width(self, line_width: int = 2):
        """Set line width"""
        result = self.send_request('applyOptions', [self.id, {'lineWidth': line_width}])
        if result['success']:
            self.logger.debug(f"Line width set to {line_width}")
        else:
            self.logger.error(f"Failed to set line width to {line_width}")
        
    def set_line_style(self, line_style: int = LineStyle.SOLID):
        """Set line style"""
        result = self.send_request('applyOptions', [self.id, {'lineStyle': line_style}])
        if result['success']:
            self.logger.debug(f"Line style set to {line_style}")
        else:
            self.logger.error(f"Failed to set line style to {line_style}")
        
    def set_line_type(self, line_type: int = 0):
        """Set line type (0 = simple, 1 = step)"""
        result = self.send_request('applyOptions', [self.id, {'lineType': line_type}])
        if result['success']:
            self.logger.debug(f"Line type set to {line_type}")
        else:
            self.logger.error(f"Failed to set line type to {line_type}")
        
    def set_point_markers_visible(self, point_markers_visible: bool = False):
        """Set point markers visible"""
        result = self.send_request('applyOptions', [self.id, {'pointMarkersVisible': point_markers_visible}])
        if result['success']:
            self.logger.debug(f"Point markers visible set to {point_markers_visible}")
        else:
            self.logger.error(f"Failed to set point markers visible to {point_markers_visible}")
        
    def set_last_value_visible(self, last_value_visible: bool = True):
        """Set last value visible"""
        result = self.send_request('applyOptions', [self.id, {'lastValueVisible': last_value_visible}])
        if result['success']:
            self.logger.debug(f"Last value visible set to {last_value_visible}")
        else:
            self.logger.error(f"Failed to set last value visible to {last_value_visible}")
        
    def set_title(self, title: str = ''):
        """Set title"""
        result = self.send_request('applyOptions', [self.id, {'title': title}])
        if result['success']:
            self.logger.debug(f"Title set to {title}")
        else:
            self.logger.error(f"Failed to set title to {title}")

    def set_visible(self, visible: bool = True):
        """Set visible"""
        result = self.send_request('applyOptions', [self.id, {'visible': visible}])
        if result['success']:
            self.logger.debug(f"Visible set to {visible}")
        else:
            self.logger.error(f"Failed to set visible to {visible}")

    def set_price_line_visible(self, price_line_visible: bool = True):
        """Set price line visible"""
        result = self.send_request('applyOptions', [self.id, {'priceLineVisible': price_line_visible}])
        if result['success']:
            self.logger.debug(f"Price line visible set to {price_line_visible}")
        else:
            self.logger.error(f"Failed to set price line visible to {price_line_visible}")

    def set_price_line_width(self, price_line_width: int = 1):
        """Set price line width"""
        result = self.send_request('applyOptions', [self.id, {'priceLineWidth': price_line_width}])
        if result['success']:
            self.logger.debug(f"Price line width set to {price_line_width}")
        else:
            self.logger.error(f"Failed to set price line width to {price_line_width}")

    def set_price_line_color(self, price_line_color: str = ''):
        """Set price line color"""
        result = self.send_request('applyOptions', [self.id, {'priceLineColor': price_line_color}])
        if result['success']:
            self.logger.debug(f"Price line color set to {price_line_color}")
        else:
            self.logger.error(f"Failed to set price line color to {price_line_color}")

    def set_price_line_style(self, price_line_style: int = LineStyle.DASHED):
        """Set price line style"""
        result = self.send_request('applyOptions', [self.id, {'priceLineStyle': price_line_style}])
        if result['success']:
            self.logger.debug(f"Price line style set to {price_line_style}")
        else:
            self.logger.error(f"Failed to set price line style to {price_line_style}")

    def set_price_format_precision(self, price_format_precision: int = 2):
        """Set price format precision"""
        result = self.send_request('applyOptions', [self.id, {'priceFormat': {'precision': price_format_precision}}])
        if result['success']:
            self.logger.debug(f"Price format precision set to {price_format_precision}")
        else:
            self.logger.error(f"Failed to set price format precision to {price_format_precision}")

    def set_price_format_min_move(self, price_format_min_move: float = 0.01):
        """Set price format min move"""
        result = self.send_request('applyOptions', [self.id, {'priceFormat': {'minMove': price_format_min_move}}])
        if result['success']:
            self.logger.debug(f"Price format min move set to {price_format_min_move}")
        else:
            self.logger.error(f"Failed to set price format min move to {price_format_min_move}")
