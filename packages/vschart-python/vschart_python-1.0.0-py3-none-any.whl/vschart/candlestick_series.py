import logging

from vschart.series_base import SeriesBase
from vschart.constants import Color, LineStyle


class CandlestickSeries(SeriesBase):
    """Candlestick Series"""
    
    def __init__(self, chart, id: str):
        super().__init__(chart, id)
        
    def add_ohlcv_legend(self, x: float, y: float,
                       text_color: str = Color.WHITE,
                       font_size: int = 12,
                       font_style: str = 'normal',
                       background_color: str = None,
                       border_color: str = None,
                       border_width: int = 1,
                       border_radius: int = 3,
                       padding: int = 5) -> 'OHLCVLegend':
        """Add OHLCV legend to the candlestick series
        
        Args:
            x: X position of the legend
            y: Y position of the legend
            text_color: Text color, default is white
            font_size: Font size, default is 12
            font_style: Font style, options: 'normal', 'bold', 'italic', 'bold italic'
            background_color: Background color, default is None (transparent)
            border_color: Border color, default is None
            border_width: Border width, default is 1
            border_radius: Border radius, default is 3
            padding: Padding, default is 5
            
        Returns:
            OHLCVLegend object
        """
        self.logger.debug(f"Adding OHLCV legend to series {self.id}")
        
        options = {
            'textColor': text_color,
            'fontSize': font_size,
            'fontStyle': font_style,
            'backgroundColor': background_color,
            'borderColor': border_color,
            'borderWidth': border_width,
            'borderRadius': border_radius,
            'padding': padding,
            'position': {'x': x, 'y': y}
        }
        
        result = self.send_request("addOHLCVLegend", [self.id, options])
        if result and isinstance(result, dict) and result.get('success'):
            legend_id = result.get('id')
            self.logger.debug(f"Created OHLCV legend ID: {legend_id}")
            from vschart.ohlcv_legend import OHLCVLegend
            return OHLCVLegend(self, legend_id)
        else:
            self.logger.error(f"Failed to create OHLCV legend: {result}")
            return None
        
    def set_up_color(self, up_color: str = Color.TEAL_GREEN):
        """Set up color"""
        result = self.send_request('applyOptions', [self.id, {'upColor': up_color}])
        if result['success']:
            self.logger.debug(f"Up color set to {up_color}")
        else:
            self.logger.error(f"Failed to set up color to {up_color}")
        
    def set_down_color(self, down_color: str = Color.CORAL_RED):
        """Set down color"""
        result = self.send_request('applyOptions', [self.id, {'downColor': down_color}])
        if result['success']:
            self.logger.debug(f"Down color set to {down_color}")
        else:
            self.logger.error(f"Failed to set down color to {down_color}")
        
    def set_wick_visible(self, wick_visible: bool = True):
        """Set wick visible"""
        result = self.send_request('applyOptions', [self.id, {'wickVisible': wick_visible}])
        if result['success']:
            self.logger.debug(f"Wick visible set to {wick_visible}")
        else:
            self.logger.error(f"Failed to set wick visible to {wick_visible}")
        
    def set_wick_color(self, wick_color: str = Color.SLATE_GRAY):
        """Set wick color"""
        result = self.send_request('applyOptions', [self.id, {'wickColor': wick_color}])
        if result['success']:
            self.logger.debug(f"Wick color set to {wick_color}")
        else:
            self.logger.error(f"Failed to set wick color to {wick_color}")
        
    def set_wick_up_color(self, wick_up_color: str = Color.TEAL_GREEN):
        """Set wick up color"""
        result = self.send_request('applyOptions', [self.id, {'wickUpColor': wick_up_color}])
        if result['success']:
            self.logger.debug(f"Wick up color set to {wick_up_color}")
        else:
            self.logger.error(f"Failed to set wick up color to {wick_up_color}")
        
    def set_wick_down_color(self, wick_down_color: str = Color.CORAL_RED):
        """Set wick down color"""
        result = self.send_request('applyOptions', [self.id, {'wickDownColor': wick_down_color}])
        if result['success']:
            self.logger.debug(f"Wick down color set to {wick_down_color}")
        else:
            self.logger.error(f"Failed to set wick down color to {wick_down_color}")
        
    def set_border_visible(self, border_visible: bool = True):
        """Set border visible"""
        result = self.send_request('applyOptions', [self.id, {'borderVisible': border_visible}])
        if result['success']:
            self.logger.debug(f"Border visible set to {border_visible}")
        else:
            self.logger.error(f"Failed to set border visible to {border_visible}")
        
    def set_border_color(self, border_color: str = Color.FOREST_GREEN):
        """Set border color"""
        result = self.send_request('applyOptions', [self.id, {'borderColor': border_color}])
        if result['success']:
            self.logger.debug(f"Border color set to {border_color}")
        else:
            self.logger.error(f"Failed to set border color to {border_color}")
        
    def set_border_up_color(self, border_up_color: str = Color.TEAL_GREEN):
        """Set border up color"""
        result = self.send_request('applyOptions', [self.id, {'borderUpColor': border_up_color}])
        if result['success']:
            self.logger.debug(f"Border up color set to {border_up_color}")
        else:
            self.logger.error(f"Failed to set border up color to {border_up_color}")
        
    def set_border_down_color(self, border_down_color: str = Color.CORAL_RED):
        """Set border down color"""
        result = self.send_request('applyOptions', [self.id, {'borderDownColor': border_down_color}])
        if result['success']:
            self.logger.debug(f"Border down color set to {border_down_color}")
        else:
            self.logger.error(f"Failed to set border down color to {border_down_color}")
        
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
