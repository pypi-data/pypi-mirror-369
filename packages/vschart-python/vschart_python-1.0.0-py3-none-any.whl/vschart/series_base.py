import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union, Optional
import logging
from datetime import datetime

from vschart.types import TimeType, to_timestamp
from vschart.base import Base
from vschart.markers import SeriesMarkers
from vschart.marker_list import MarkerList
from vschart.custom_marker import CustomMarker
from vschart.background_color import BackgroundColor
from vschart.trend_line import TrendLine
from vschart.fibonacci import Fibonacci
from vschart.rectangle import Rectangle
from vschart.vertical_line import VerticalLine
from vschart.volume_profile import VolumeProfile
from vschart.tooltip import Tooltip
from vschart.constants import MarkerPosition, MarkerShape, Color, Size

class SeriesBase(Base):
    """Base class for all series types"""
    
    def __init__(self, chart, id: str):
        super().__init__()
        self.chart = chart
        self.id = id
        self.logger.debug(f"{self.__class__.__name__} created, ID: {id}")
        
    def send_request(self, method: str, params: List[Any] = None) -> Any:
        """Send request to the chart"""
        return self.chart.send_request(method, params)
    
    def set_data(self, data) -> bool:
        """Set series data from DataFrame or list of dictionaries"""
        if isinstance(data, pd.DataFrame):
            data_dict = data.to_dict(orient='records')
        elif isinstance(data, list):
            data_dict = data
        else:
            raise TypeError(f"Data must be pandas DataFrame or list, got {type(data)}")
        
        self.logger.debug(f"Setting data for series {self.id}, {len(data_dict)} data points added")
        if data_dict and len(data_dict) > 0:
            self.logger.debug(f"First data point: {data_dict[0]}")
        
        return self.send_request("setData", [self.id, data_dict])
    
    def update(self, bar: np.ndarray, historical_update: bool = False) -> bool:
        """Update series data"""
        bar_list = bar.tolist()
        self.logger.debug(f"Updating series {self.id} with {bar_list}")
        return self.send_request('updateSeries', [self.id, bar_list, historical_update])
    
    def delete(self):
        self.send_request('removeSeries', [self.id])
    
    def add_marker(self, time: TimeType, position: str = MarkerPosition.BELOW_BAR, shape: str = MarkerShape.ARROW_UP, color: int = Color.RED, size: int = Size.M, text: str = '') -> SeriesMarkers:
        markers = MarkerList()
        markers.add_marker(time, position, shape, color, size, text)
        return self.add_marker_list(markers)

    def add_marker_list(self, markers: MarkerList) -> SeriesMarkers:
        # must sort for lightweight-charts to work properly
        markers.sort()
        self.logger.debug(f"Adding markers to series {self.id}: {len(markers.list)} markers")
        if markers.list and len(markers.list) > 0:
            self.logger.debug(f"First marker: {markers.list[0]}")

        result = self.send_request('addSeriesMarkers', [self.id, markers.list])
        markers_id = result.get('id') if isinstance(result, dict) else result 
        self.logger.debug(f"Markers added to series {self.id}, ID: {markers_id}")
        return SeriesMarkers(self, markers_id)
    
    def add_trend_line(self,
        start_time: TimeType, start_price: float, 
        end_time: TimeType, end_price: float, 
        line_color: str = Color.BLUE, 
        width: int = 6, 
        line_style: int = 0,
        show_labels: bool = True,
        label_background_color: str = Color.TRANS_WHITE,
        label_text_color: str = Color.BLACK) -> 'TrendLine':
        self.logger.debug(f"Adding trend line to series {self.id}")
        options = {
            'lineColor': line_color,
            'width': width,
            'lineStyle': line_style,
            'showLabels': show_labels,
            'labelBackgroundColor': label_background_color,
            'labelTextColor': label_text_color,
        }
        result = self.send_request("addTrendLine", [self.id, to_timestamp(start_time), start_price, to_timestamp(end_time), end_price, options or {}])
        if result['success']:
            trend_line_id = result.get('id') if isinstance(result, dict) else result
            self.logger.debug(f"Created trend line ID: {trend_line_id}")
            return TrendLine(self, trend_line_id)
        else:
            self.logger.error(f"Failed to create trend line: {result}")
            return None
    
    def add_fibonacci(self, start_time: TimeType, start_price: float, end_time: TimeType, end_price: float, 
                     trend_line_color: str = Color.BLACK,
                     trend_line_width: int = 2,
                     fib_colors: List[str] = None,
                     fib_line_width: int = 1,
                     fill_colors: List[str] = None,
                     show_fill: bool = True,
                     fill_opacity: float = 0.1,
                     coefficients: List[float] = None,
                     extension_bars: int = -1,
                     show_labels: bool = True,
                     label_background_color: str = Color.WHITE,
                     label_text_color: str = Color.BLACK,
                     label_font_size: int = 12,
                     label_position: str = 'left') -> 'Fibonacci':
        """Add a fibonacci retracement to the chart"""
        self.logger.debug(f"Adding fibonacci to series {self.id}")
        
        if fib_colors is None:
            fib_colors = [
                Color.RED,        # 0%
                Color.ORANGE,     # 38.2%
                Color.YELLOW,     # 61.8%
                Color.GREEN,      # 100%
                Color.BLUE        # 161.8%
            ]
        
        if fill_colors is None:
            fill_colors = [
                'rgba(255, 0, 0, 0.1)',     # Light red fill
                'rgba(255, 165, 0, 0.1)',   # Light orange fill
                'rgba(255, 255, 0, 0.1)',   # Light yellow fill
                'rgba(0, 255, 0, 0.1)',     # Light green fill
                'rgba(0, 0, 255, 0.1)'      # Light blue fill
            ]
        
        if coefficients is None:
            coefficients = [0, 0.382, 0.618, 1, 1.618]
        
        options = {
            'trendLineColor': trend_line_color,
            'trendLineWidth': trend_line_width,
            'fibColors': fib_colors,
            'fibLineWidth': fib_line_width,
            'fillColors': fill_colors,
            'showFill': show_fill,
            'fillOpacity': fill_opacity,
            'coefficients': coefficients,
            'extensionBars': extension_bars,
            'showLabels': show_labels,
            'labelBackgroundColor': label_background_color,
            'labelTextColor': label_text_color,
            'labelFontSize': label_font_size,
            'labelPosition': label_position,
        }
        
        result = self.send_request("addFibonacci", [self.id, to_timestamp(start_time), start_price, to_timestamp(end_time), end_price, options or {}])
        if result['success']:
            fibonacci_id = result.get('id') if isinstance(result, dict) else result
            self.logger.debug(f"Created fibonacci ID: {fibonacci_id}")
            return Fibonacci(self, fibonacci_id)
        else:
            self.logger.error(f"Failed to create fibonacci: {result}")
            return None
    
    def add_rectangle(self, start_time: TimeType, start_price: float, end_time: TimeType, end_price: float, 
                     text: str = '',
                     border_color: str = Color.BLACK,
                     border_width: int = 2,
                     line_style: str = 'solid',
                     fill_color: str = Color.TRANS_BLUE,
                     show_text: bool = True,
                     text_position: str = 'inside',
                     text_color: str = Color.BLACK,
                     text_background_color: str = Color.TRANS_WHITE,
                     text_size: int = 12,
                     text_font: str = 'Arial') -> 'Rectangle':
        """Add a rectangle to the chart"""
        self.logger.debug(f"Adding rectangle to series {self.id}")
        
        options = {
            'borderColor': border_color,
            'borderWidth': border_width,
            'lineStyle': line_style,
            'fillColor': fill_color,
            'showText': show_text,
            'textPosition': text_position,
            'textColor': text_color,
            'textBackgroundColor': text_background_color,
            'textSize': text_size,
            'textFont': text_font,
        }
        
        result = self.send_request("addRectangle", [self.id, to_timestamp(start_time), start_price, to_timestamp(end_time), end_price, text, options or {}])
        if result['success']:
            rectangle_id = result.get('id') if isinstance(result, dict) else result
            self.logger.debug(f"Created rectangle ID: {rectangle_id}")
            return Rectangle(self, rectangle_id)
        else:
            self.logger.error(f"Failed to create rectangle: {result}")

    def add_custom_marker(self, time: TimeType, price: float, shape: str = MarkerShape.STAR,
                         color: str = Color.BLUE, size: int = Size.M, text: str = '',
                         text_color: str = Color.BLACK, text_size: int = 12,
                         text_position: str = 'above') -> 'CustomMarker':

        self.logger.debug(f"Adding custom marker to series {self.id}")
        
        options = {
            'shape': shape,
            'color': color,
            'size': size,
            'text': text,
            'textColor': text_color,
            'textSize': text_size,
            'textPosition': text_position,
        }
        
        result = self.send_request("addCustomMarker", [self.id, to_timestamp(time), price, options])
        if result['success']:
            marker_id = result.get('id') if isinstance(result, dict) else result
            self.logger.debug(f"Created custom marker ID: {marker_id}")
            return CustomMarker(self, marker_id)
        else:
            self.logger.error(f"Failed to create custom marker: {result}")
    
    def add_vertical_line(self, time: TimeType,
                         color: str = Color.GREEN,
                         label_text: str = '',
                         width: int = 3,
                         label_background_color: str = Color.GREEN,
                         label_text_color: str = Color.WHITE,
                         show_label: bool = False) -> 'VerticalLine':
        """Add a vertical line to the chart"""
        self.logger.debug(f"Adding vertical line to series {self.id}")
        
        options = {
            'color': color,
            'labelText': label_text,
            'width': width,
            'labelBackgroundColor': label_background_color,
            'labelTextColor': label_text_color,
            'showLabel': show_label
        }
        
        result = self.send_request("addVerticalLine", [self.id, to_timestamp(time), options or {}])
        if result['success']:
            vertical_line_id = result.get('id') if isinstance(result, dict) else result
            self.logger.debug(f"Created vertical line ID: {vertical_line_id}")
            return VerticalLine(self, vertical_line_id)
        else:
            self.logger.error(f"Failed to create vertical line: {result}")
            return None
    
    def add_volume_profile(self, data: List[Dict[str, float]], start_time: TimeType, end_time: TimeType,
                          fill_color: str = Color.VOLUME_BLUE_FILL,
                          bar_color: str = Color.VOLUME_BLUE_BAR,
                          opacity: float = 0.8,
                          background_color: str = 'rgba(200, 200, 200, 0.1)',
                          border_color: str = 'rgba(100, 100, 100, 0.3)',
                          border_width: int = 1,
                          number_of_bins: int = 20) -> 'VolumeProfile':
        """Add a volume profile to the chart
        
        Args:
            data: List of price and volume data, each item should contain 'price' and 'volume' keys
            start_time: Start time of the volume profile period
            end_time: End time of the volume profile period
            fill_color: Fill color for volume bars
            bar_color: Color for volume bars
            opacity: Opacity of the volume profile
            background_color: Background color spanning the time period
            border_color: Border color for the volume profile area
            border_width: Width of the border
            number_of_bins: Number of histogram bins
        """
        self.logger.debug(f"Adding volume profile to series {self.id}")
        
        options = {
            'fillColor': fill_color,
            'barColor': bar_color,
            'opacity': opacity,
            'backgroundColor': background_color,
            'borderColor': border_color,
            'borderWidth': border_width,
            'numberOfBins': number_of_bins,
        }
        
        result = self.send_request("addVolumeProfile", [self.id, data, to_timestamp(start_time), to_timestamp(end_time), options or {}])
        if result['success']:
            volume_profile_id = result.get('id') if isinstance(result, dict) else result
            self.logger.debug(f"Created volume profile ID: {volume_profile_id}")
            return VolumeProfile(self, volume_profile_id)
        else:
            self.logger.error(f"Failed to create volume profile: {result}")
            return None
    
    def add_background_color(self, data: List[Dict[TimeType, Union[int, float, str]]] = None) -> BackgroundColor:
        self.logger.debug(f"Adding background color to series {self.id}")
        if data:
            data = [{'time': to_timestamp(item['time']), 'color': item['color']} for item in data]
        result = self.send_request("addBackgroundColor", [self.id, data or []])
        if result['success']:
            background_color_id = result['id']
            self.logger.debug(f"Created background color ID: {background_color_id}")
            return BackgroundColor(self, background_color_id)
        else:
            self.logger.error(f"Failed to create background color: {result['error']}")
            return None
    
    def add_legend(self, x: float, y: float, items: List[Dict[str, Any]],
                  text_color: str = Color.WHITE,
                  font_size: int = 12,
                  font_style: str = 'normal',
                  background_color: Optional[str] = None,
                  border_color: Optional[str] = None,
                  border_width: int = 1,
                  border_radius: int = 3,
                  padding: int = 5) -> 'Legend':
        """添加图例到图表

        Args:
            x: 图例的x坐标
            y: 图例的y坐标
            items: 图例项列表，每个项包含text和可选的样式属性
            text_color: 文本颜色，默认为白色
            font_size: 字体大小，默认为12
            font_style: 字体样式，可选值: 'normal', 'bold', 'italic', 'bold italic'
            background_color: 背景颜色，默认为None(透明)
            border_color: 边框颜色，默认为None
            border_width: 边框宽度，默认为1
            border_radius: 边框圆角半径，默认为3
            padding: 内边距大小，默认为5
        """
        self.logger.debug(f"Adding legend to series {self.id}")

        options = {
            'textColor': text_color,
            'fontSize': font_size,
            'fontStyle': font_style,
            'backgroundColor': background_color,
            'borderColor': border_color,
            'borderWidth': border_width,
            'borderRadius': border_radius,
            'padding': padding,
        }

        result = self.send_request("addLegend", [self.id, x, y, items, options or {}])
        if result['success']:
            legend_id = result.get('id') if isinstance(result, dict) else result
            self.logger.debug(f"Created legend ID: {legend_id}")
            return Legend(self, legend_id)
        else:
            self.logger.error(f"Failed to create legend: {result}")
            return None
            
    def add_tooltip(self, options: Dict[str, Any] = None) -> Tooltip:
        """Add tooltip to the series
        
        Args:
            options: Optional tooltip configuration options
            
        Returns:
            Tooltip: The created tooltip object
            
        Raises:
            Exception: If tooltip creation fails
        """
        if options is None:
            options = {}
            
        result = self.send_request("addTooltip", [self.id, options])
        if result['success']:
            self.logger.debug(f"Tooltip added to series {self.id}")
            return Tooltip(self, result['id'])
        else:
            self.logger.error(f"Failed to add tooltip to series {self.id}: {result.get('error', 'Unknown error')}")
            raise Exception(f"Failed to add tooltip: {result.get('error', 'Unknown error')}")

    def remove_primitive(self, primitive_id: str) -> bool:
        """Remove series primitive"""
        self.logger.debug(f"Removing series primitive {primitive_id}")
        return self.send_request("removeSeriesPrimitive", [self.id, primitive_id])
    


