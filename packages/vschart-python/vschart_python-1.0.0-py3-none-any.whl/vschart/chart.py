import json
import re
import time
from typing import Dict, Any, Optional, List, Union
from webbrowser import BackgroundBrowser
import websocket
import threading
from rich.logging import RichHandler
import logging

from vschart.base import Base
from vschart.candlestick_series import CandlestickSeries
from vschart.volume_series import VolumeSeries
from vschart.line_series import LineSeries
from vschart.constants import Color, LineStyle, LineType, PriceLineStyle, LastPriceAnimationMode, CrosshairMode
from vschart.types import TimeType, to_timestamp

class Chart(Base):

    def __init__(self, host: str = "localhost", port: int = 8082):
        super().__init__()
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"
        self.ws = None
        self.message_id = 0
        self.pending_requests = {}
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to VSCode plugin WebSocket server"""
        try:
            self.logger.debug(f"Connecting to {self.url}")
            self.ws = websocket.WebSocketApp(
                self.url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            self.logger.debug("Waiting for connection...")
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if self.connected:
                self.logger.debug("Connection successful!")
            else:
                self.logger.warning("Connection timeout!")
                
            return self.connected
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Connection failed: {error_msg}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.ws:
            self.logger.debug("Disconnecting...")
            self.ws.close()
            self.connected = False
            self.logger.debug("Disconnected")
    
    def _on_open(self, ws):
        """WebSocket connection successful callback"""
        self.connected = True
        self.logger.debug("Connected to VSCode chart plugin")
    
    def _on_message(self, ws, message):
        """Message received callback"""
        try:
            data = json.loads(message)
            self.logger.debug(f"Received message: {json.dumps(data, indent=2)}")
            
            # Process API response
            if 'id' in data and data['id'] in self.pending_requests:
                # If API response is missing result field, add default result
                if data.get('type') == 'api_response' and 'result' not in data:
                    method = self.pending_requests[data['id']].get('method')
                    self.logger.debug(f"Response missing result field for method: {method}")
                    
                    # Add default results for different methods
                    if method == 'addCandlestickSeries':
                        data['result'] = {'id': 'candlestick_0', 'type': 'candlestick'}
                    elif method == 'addVolumeSeries':
                        data['result'] = {'id': 'histogram_1', 'type': 'histogram'}
                    elif method == 'addLineSeries':
                        data['result'] = {'id': 'line_0', 'type': 'line'}
                
                self.pending_requests[data['id']]['response'] = data
                self.pending_requests[data['id']]['event'].set()
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
    
    def _on_error(self, ws, error):
        """Error callback"""
        self.logger.error(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Connection closed callback"""
        self.connected = False
        self.logger.debug(f"Connection to VSCode chart plugin closed (status code: {close_status_code})")
    
    def send_request(self, method: str, params: List[Any] = None) -> Any:
        """Send API request"""
        if not self.connected:
            raise ConnectionError("Not connected to chart plugin")
        
        self.message_id += 1
        message_id = str(self.message_id)
        
        message = {
            "type": "api_call",
            "method": method,
            "params": params or [],
            "id": message_id
        }
        
        event = threading.Event()
        self.pending_requests[message_id] = {
            "event": event,
            "response": None,
            "method": method  # Store method name for adding default results in response
        }
        
        self.logger.debug(f"Sending API call: {method}\n{json.dumps(message, indent=2)}")
        
        self.ws.send(json.dumps(message))
        
        # Wait for response
        self.logger.debug(f"Waiting for {method} response...")
        if event.wait(timeout=10):
            response = self.pending_requests[message_id]['response']
            del self.pending_requests[message_id]
            
            if response.get('type') == 'error':
                error_msg = response.get('error', 'Unknown error')
                self.logger.error(f"API error: {error_msg}")
                raise Exception(error_msg)
            
            return response.get('result')
        else:
            del self.pending_requests[message_id]
            self.logger.error("API call timeout")
            raise TimeoutError("API call timeout")
        
    def create(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create chart"""
        result = self.send_request("createChart", options or {})
        if result['success']:
            self.logger.debug(f"Chart created with id {result['id']}")
            self.id = result['id']
        else:
            self.logger.error("Failed to create chart")
            
    def apply_default_chart_options(self):
        """Apply default chart options"""
        result = self.send_request("applyDefaultChartOptions")
        if result['success']:
            self.logger.debug(f"Default chart options applied")
        else:
            self.logger.error(f"Failed to apply default chart options")
        
    def set_separator_color(self, separator_color: str = Color.RED):
        """Set separator color"""
        result = self.send_request("applyOptions", [self.id,  {'layout': {'panes': {'separatorColor': separator_color}}}])
        if result['success']:
            self.logger.debug(f"Separator color set to {separator_color}")
        else:
            self.logger.error(f"Failed to set separator color to {separator_color}")
        
    def set_separator_hover_color(self, separator_hover_color: str = Color.RED):
        """Set separator hover color"""
        result = self.send_request("applyOptions", [self.id, {'layout': {'panes': {'separatorHoverColor': separator_hover_color}}}])
        if result['success']:
            self.logger.debug(f"Separator hover color set to {separator_hover_color}")
        else:
            self.logger.error(f"Failed to set separator hover color to {separator_hover_color}")
    
    def set_enable_resize(self, enable_resize: bool = False):
        """Set enable resize"""
        result = self.send_request("applyOptions", [self.id, {'layout': {'panes': {'enableResize': enable_resize}}}])
        if result['success']:
            self.logger.debug(f"Enable resize set to {enable_resize}")
        else:
            self.logger.error(f"Failed to set enable resize to {enable_resize}")
    
    def set_width(self, width: int = 0):
        """Set width"""
        result = self.send_request("applyOptions", [self.id, {'width': width}])
        if result['success']:
            self.logger.debug(f"Width set to {width}")
        else:
            self.logger.error(f"Failed to set width to {width}")

    def set_height(self, height: int = 0):
        """Set height"""
        result = self.send_request("applyOptions", [self.id, {'height': height}])
        if result['success']:
            self.logger.debug(f"Height set to {height}")
        else:
            self.logger.error(f"Failed to set height to {height}")

    def set_auto_size(self, auto_size: bool = True):
        """Set auto size"""
        result = self.send_request("applyOptions", [self.id, {'autoSize': auto_size}])
        if result['success']:
            self.logger.debug(f"Auto size set to {auto_size}")
        else:
            self.logger.error(f"Failed to set auto size to {auto_size}")
        
    def set_add_default_pane(self, add_default_pane: bool = True):
        """Set add default pane"""
        result = self.send_request("applyOptions", [self.id, {'addDefaultPane': add_default_pane}])
        if result['success']:
            self.logger.debug(f"Add default pane set to {add_default_pane}")
        else:
            self.logger.error(f"Failed to set add default pane to {add_default_pane}")

    def set_background(self, type: str = 'solid', color: str = Color.WHITE):
        """Set background"""
        result = self.send_request('applyOptions', [self.id, {'layout': {'background': {'type': type, 'color': color}}}])
        if result['success']:
            self.logger.debug(f"Background type set to {type}, color to {color}")
        else:
            self.logger.error(f"Failed to set background type to {type}, color to {color}")

    def set_text_color(self, text_color: str = Color.DARK_GRAY):
        """Set text color"""
        result = self.send_request("applyOptions", [self.id, {'layout': {'textColor': text_color}}])
        if result['success']:
            self.logger.debug(f"Text color set to {text_color}")
        else:
            self.logger.error(f"Failed to set text color to {text_color}")

    def set_font_size(self, font_size: int = 12):
        """Set font size"""
        result = self.send_request("applyOptions", [self.id, {'layout': {'fontSize': font_size}}])
        if result['success']:
            self.logger.debug(f"Font size set to {font_size}")
        else:
            self.logger.error(f"Failed to set font size to {font_size}")
        
    def set_font_family(self, font_family: str = '-apple-system'):
        """Set font family"""
        result = self.send_request("applyOptions", [self.id, {'layout': {'fontFamily': font_family}}])
        if result['success']:
            self.logger.debug(f"Font family set to {font_family}")
        else:
            self.logger.error(f"Failed to set font family to {font_family}")
            
    def set_pane_height(self, pane: int, height: int):
        result = self.send_request("setPaneHeight", [pane, height])
        if result['success']:
            self.logger.debug(f"Pane height set to {height}")
        else:
            self.logger.error(f"Failed to set pane height to {height}")
            
    def set_crosshair_mode(self, mode: int = CrosshairMode.NORMAL):
        """Set crosshair mode"""
        result = self.send_request("applyOptions", [self.id, {'crosshair': {'mode': mode}}])
        if result['success']:
            self.logger.debug(f"Crosshair mode set to {mode}")
        else:
            self.logger.error(f"Failed to set crosshair mode to {mode}")
            
    def set_crosshair_line_style(self, horizontal: bool = True, line_style: int = LineStyle.DASHED):
        """Set crosshair line style"""
        if horizontal:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'horzLine': {'style': line_style}}}])
        else:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'vertLine': {'style': line_style}}}])
        if result['success']:
            self.logger.debug(f"Crosshair line style set to {line_style}")
        else:
            self.logger.error(f"Failed to set crosshair line style to {line_style}")
            
    def set_crosshair_line_width(self, horizontal: bool = True, line_width: int = 1):
        """Set crosshair line width"""
        if horizontal:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'horzLine': {'width': line_width}}}])
        else:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'vertLine': {'width': line_width}}}])
        if result['success']:
            self.logger.debug(f"Crosshair line width set to {line_width}")
        else:
            self.logger.error(f"Failed to set crosshair line width to {line_width}")
            
    def set_crosshair_line_color(self, horizontal: bool = True, line_color: str = Color.WHITE):
        """Set crosshair line color"""
        if horizontal:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'horzLine': {'color': line_color}}}])
        else:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'vertLine': {'color': line_color}}}])
        if result['success']:
            self.logger.debug(f"Crosshair line color set to {line_color}")
        else:
            self.logger.error(f"Failed to set crosshair line color to {line_color}")
            
    def set_crosshair_line_visible(self, horizontal: bool = True, visible: bool = True):
        """Set crosshair line visible"""
        if horizontal:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'horzLine': {'visible': visible}}}])
        else:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'vertLine': {'visible': visible}}}])
        if result['success']:
            self.logger.debug(f"Crosshair line visible set to {visible}")
        else:
            self.logger.error(f"Failed to set crosshair line visible to {visible}")
            
    def set_crosshair_line_label_visible(self, horizontal: bool = True, visible: bool = True):
        """Set crosshair line label visible"""
        if horizontal:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'horzLine': {'labelVisible': visible}}}])
        else:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'vertLine': {'labelVisible': visible}}}])
        if result['success']:
            self.logger.debug(f"Crosshair line label visible set to {visible}")
        else:
            self.logger.error(f"Failed to set crosshair line label visible to {visible}")
            
    def set_crosshair_label_background_color(self, horizontal: bool = True, background_color: str = Color.GREEN):
        """Set crosshair label background color"""
        if horizontal:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'horzLine': {'labelBackgroundColor': background_color}}}])
        else:
            result = self.send_request("applyOptions", [self.id, {'crosshair': {'vertLine': {'labelBackgroundColor': background_color}}}])
        if result['success']:
            self.logger.debug(f"Crosshair label background color set to {background_color}")
        else:
            self.logger.error(f"Failed to set crosshair label background color to {background_color}")
    
    def add_candlestick_series(
        self, pane: int = 0,
        up_color: str = Color.TEAL_GREEN, down_color: str = Color.CORAL_RED,
        wick_visible: bool = True, wick_color: str = Color.SLATE_GRAY,
        wick_up_color: str = Color.TEAL_GREEN, wick_down_color: str = Color.CORAL_RED,
        border_visible: bool = True, border_color: str = Color.FOREST_GREEN,
        border_up_color: str = Color.TEAL_GREEN, border_down_color: str = Color.CORAL_RED,
        last_value_visible: bool = True,
        title: str = '',
        visible: bool = True,
        price_line_visible: bool = True,
        price_line_width: int = 1,
        price_line_color: str = '', # default: last bar color
        price_line_style: int = LineStyle.DASHED,
        price_format_precision: int = 2,
        price_format_min_move: float = 0.01
        ) -> CandlestickSeries:
        self.logger.debug(f"Adding candlestick series to pane {pane}")
        options = {
            'upColor': up_color,
            'downColor': down_color,
            'wickVisible': wick_visible,
            'wickColor': wick_color,
            'wickUpColor': wick_up_color,
            'wickDownColor': wick_down_color,
            'borderVisible': border_visible,
            'borderColor': border_color,
            'borderUpColor': border_up_color,
            'borderDownColor': border_down_color,
            'lastValueVisible': last_value_visible,
            'title': title,
            'visible': visible,
            'priceLineVisible': price_line_visible,
            'priceLineWidth': price_line_width,
            'priceLineColor': price_line_color,
            'priceLineStyle': price_line_style,
            'priceFormat': {
                'type': 'price',
                'precision': price_format_precision,
                'minMove': price_format_min_move
            }
        }
        result = self.send_request("addCandlestickSeries", [pane, options])
        series_id = result.get('id') if isinstance(result, dict) else result
        self.logger.debug(f"Created series ID: {series_id}")
        return CandlestickSeries(self, series_id)
    
    def add_histogram_series(
        self,
        pane: int = 1,
        color: str = Color.TRANS_BLUE,
        scale_margin_top: float = 0.8, scale_margin_bottom: float = 0.0,
        title: str = '',
        visible: bool = True,
        price_line_visible: bool = True,
        price_line_width: int = 1,
        price_line_color: str = '', # default: last bar color
        price_line_style: int = LineStyle.DASHED,
        price_format_precision: int = 2,
        price_format_min_move: float = 0.01
        ) -> VolumeSeries:
        self.logger.debug(f"Adding histogram series to pane {pane}")
        options = {
            'color': color,
            'scaleMargins': {
                'top': scale_margin_top,
                'bottom': scale_margin_bottom,
            },
            'title': title,
            'visible': visible,
            'priceLineVisible': price_line_visible,
            'priceLineWidth': price_line_width,
            'priceLineColor': price_line_color,
            'priceLineStyle': price_line_style,
            'priceFormat': {
                'type': 'volume',
                'precision': price_format_precision,
                'minMove': price_format_min_move
            },
        }
        result = self.send_request("addVolumeSeries", [pane, options])
        series_id = result.get('id') if isinstance(result, dict) else result
        self.logger.debug(f"Created series ID: {series_id}")
        return VolumeSeries(self, series_id)
    
    def add_line_series(
        self,
        pane: int = 0,
        color: str = Color.BRIGHT_BLUE,
        line_style: int = LineStyle.SOLID,
        line_width: int = 3,
        line_type: int = LineType.SIMPLE,
        line_visible: bool = True,
        point_markers_visible: bool = False,
        crosshair_marker_visible: bool = True,
        crosshair_marker_radius: int = 4,
        crosshair_marker_border_color: str = '',
        crosshair_marker_background_color: str = '',
        crosshair_marker_border_width: int = 2,
        last_price_animation: int = LastPriceAnimationMode.DISABLED,
        title: str = '',
        visible: bool = True,
        price_line_visible: bool = True,
        price_line_width: int = 1,
        price_line_color: str = '', # default: last bar color
        price_line_style: int = LineStyle.DASHED,
        price_format_precision: int = 2,
        price_format_min_move: float = 0.01
    ) -> LineSeries:
        self.logger.debug(f"Adding line series to pane {pane}")
        options = {
            'color': color,
            'lineStyle': line_style,
            'lineWidth': line_width,
            'lineType': line_type,
            'lineVisible': line_visible,
            'pointMarkersVisible': point_markers_visible,
            'crosshairMarkerVisible': crosshair_marker_visible,
            'crosshairMarkerRadius': crosshair_marker_radius,
            'crosshairMarkerBorderColor': crosshair_marker_border_color,
            'crosshairMarkerBackgroundColor': crosshair_marker_background_color,
            'crosshairMarkerBorderWidth': crosshair_marker_border_width,
            'lastPriceAnimation': last_price_animation,
            'title': title,
            'visible': visible,
            'priceLineVisible': price_line_visible,
            'priceLineWidth': price_line_width,
            'priceLineColor': price_line_color,
            'priceLineStyle': price_line_style,
            'priceFormat': {
                'type': 'price',
                'precision': price_format_precision,
                'minMove': price_format_min_move
            }
        }
        result = self.send_request("addLineSeries", [pane, options])
        series_id = result.get('id') if isinstance(result, dict) else result
        self.logger.debug(f"Created series ID: {series_id}")
        return LineSeries(self, series_id)
    
    def get_visible_range(self) -> Dict[str, Any]:
        """Get visible range"""
        self.logger.debug("Getting visible range")
        result = self.send_request("getVisibleRange")
        if result['success']:
            self.logger.debug(f"Visible range: {result['range']}")
        return result['range']
    
    def set_visible_range(self, start_time: TimeType, end_time: TimeType) -> bool:
        """Set visible range"""
        start_timestamp = to_timestamp(start_time)
        end_timestamp = to_timestamp(end_time)
        self.logger.debug(f"Setting visible range from {start_timestamp} to {end_timestamp}")
        result = self.send_request("setVisibleRange", [{"from": start_timestamp, "to": end_timestamp}])
        return result['success']
    
    def fit_content(self) -> bool:
        """Fit content"""
        self.logger.debug("Fitting content")
        result = self.send_request("fitContent")
        return result['success']
    
    def reset_time_scale(self) -> bool:
        """Reset time scale"""
        self.logger.debug("Resetting time scale")
        result = self.send_request("resetTimeScale")
        return result['success']
    
    def clear_chart(self) -> bool:
        """Clear chart"""
        self.logger.debug("Clearing chart")
        result = self.send_request("clearChart")
        return result['success']
