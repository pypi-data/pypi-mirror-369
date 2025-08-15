"""
Custom Marker implementation for VSChart Python package.

This module provides the CustomMarker class for adding custom markers
to chart series with various shapes and positions.
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime
import json

from vschart.series_primitive import SeriesPrimitive
from vschart.constants import MarkerShape, Color

class CustomMarker(SeriesPrimitive):
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__(series, id)
        
    def set_shape(self, shape: str = MarkerShape.DIAMOND):
        """Set marker shape"""
        result = self.send_request('applyOptions', [self.id, {'shape': shape}])
        if result['success']:
            self.logger.debug(f"Shape set to {shape}")
        else:
            self.logger.error(f"Failed to set shape to {shape}")
            
    def set_color(self, color: str = Color.RED):
        """Set marker color"""
        result = self.send_request('applyOptions', [self.id, {'color': color}])
        if result['success']:
            self.logger.debug(f"Color set to {color}")
        else:
            self.logger.error(f"Failed to set color to {color}")
            
    def set_size(self, size: int = 12):
        """Set marker size"""
        result = self.send_request('applyOptions', [self.id, {'size': size}])
        if result['success']:
            self.logger.debug(f"Size set to {size}")
        else:
            self.logger.error(f"Failed to set size to {size}")

    def set_text(self, text: str = ''):
        """Set marker text"""
        result = self.send_request('applyOptions', [self.id, {'text': text}])
        if result['success']:
            self.logger.debug(f"Text set to {text}")
        else:
            self.logger.error(f"Failed to set text to {text}")
            
    def set_text_position(self, position: str = 'above'):
        """Set text position relative to marker (above or below)"""
        if position not in ['above', 'below']:
            self.logger.error(f"Invalid text position: {position}. Must be 'above' or 'below'.")
            return
            
        result = self.send_request('applyOptions', [self.id, {'textPosition': position}])
        if result['success']:
            self.logger.debug(f"Text position set to {position}")
        else:
            self.logger.error(f"Failed to set text position to {position}")
        