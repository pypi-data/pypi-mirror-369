import logging

from vschart.series_base import SeriesBase
from vschart.constants import Color, LineStyle


class VolumeSeries(SeriesBase):
    """Volume Histogram Series"""
    
    def __init__(self, chart, id: str):
        super().__init__(chart, id)
        
    def set_color(self, color: str = Color.TEAL_GREEN):
        """Set color"""
        result = self.send_request('applyOptions', [self.id, {'color': color}])
        if result['success']:
            self.logger.debug(f"Color set to {color}")
        else:
            self.logger.error(f"Failed to set color to {color}")
        
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

    def set_price_format_precision(self, price_format_precision: int = 0):
        """Set price format precision"""
        result = self.send_request('applyOptions', [self.id, {'priceFormat': {'precision': price_format_precision}}])
        if result['success']:
            self.logger.debug(f"Price format precision set to {price_format_precision}")
        else:
            self.logger.error(f"Failed to set price format precision to {price_format_precision}")

    def set_price_format_min_move(self, price_format_min_move: float = 1.0):
        """Set price format min move"""
        result = self.send_request('applyOptions', [self.id, {'priceFormat': {'minMove': price_format_min_move}}])
        if result['success']:
            self.logger.debug(f"Price format min move set to {price_format_min_move}")
        else:
            self.logger.error(f"Failed to set price format min move to {price_format_min_move}")
