#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Marker Test
Testing custom marker addition, styling configuration, and deletion functionality
"""

import argparse
import time
import logging
from typing import List, Dict, Any

from vschart.constants import MarkerShape, Color, Size, TextPosition
from vschart import Chart, CandlestickSeries, CustomMarker
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()

def test_custom_marker(candlestick_series: CandlestickSeries, volume_series,
                       candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                       delay: float, interactive_mode: bool) -> None:
    """
    Test custom marker addition, styling configuration, and deletion functionality
    
    Args:
        candlestick_series: Candlestick series object
        volume_series: Volume series object
        candlestick_data: Candlestick chart data
        volume_data: Volume chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting custom marker functionality test...")
    custom_markers = []
    
    # Custom Marker 1: Star shape, red color, large size
    logging.info("Adding custom marker 1: Star shape, red color, large size...")
    marker_1 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 1 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 1 // 10]['high'] * 1.02,
        shape=MarkerShape.STAR,
        color=Color.RED,
        size=Size.L,
        text="Bullish Star"
    )
    custom_markers.append(marker_1)
    pause_for_next("Custom marker 1 added.", interactive_mode, delay * 2)
    
    # Custom Marker 2: Diamond shape, green color, medium size
    logging.info("Adding custom marker 2: Diamond shape, green color, medium size...")
    marker_2 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 3 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 3 // 10]['low'] * 0.98,
        shape=MarkerShape.DIAMOND,
        color=Color.GREEN,
        size=Size.M,
        text="Bearish Diamond"
    )
    custom_markers.append(marker_2)

    pause_for_next("Custom marker 2 added.", interactive_mode, delay * 2)
    
    # Custom Marker 3: Triangle shape, blue color, small size
    logging.info("Adding custom marker 3: Triangle shape, blue color, small size...")
    marker_3 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 5 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 5 // 10]['close'],
        shape=MarkerShape.TRIANGLE_UP,
        color=Color.BLUE,
        size=Size.S,
        text="Support Triangle"
    )
    custom_markers.append(marker_3)

    pause_for_next("Custom marker 3 added.", interactive_mode, delay * 2)
    
    # Custom Marker 4: Ring shape, orange color, medium size
    logging.info("Adding custom marker 4: Ring shape, orange color, medium size...")
    marker_4 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 7 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 7 // 10]['high'] * 1.01,
        shape=MarkerShape.RING,
        color=Color.ORANGE,
        size=Size.XXXL,
        text="Resistance Ring"
    )
    custom_markers.append(marker_4)

    pause_for_next("Custom marker 4 added.", interactive_mode, delay * 2)
    
    # Custom Marker 5: Star shape, purple color, with custom text styling (text above)
    logging.info("Adding custom marker 5: Star shape, purple color, with custom text styling (text above)...")
    marker_5 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 9 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 9 // 10]['low'] * 0.99,
        shape=MarkerShape.STAR,
        color=Color.PURPLE,
        size=Size.L,
        text="Reversal Signal",
        text_color=Color.WHITE,
        text_size=14,
        text_position=TextPosition.ABOVE
    )
    custom_markers.append(marker_5)

    pause_for_next("Custom marker 5 added.", interactive_mode, delay * 2)
    
    # Custom Marker 6: Diamond shape, red color, with text below
    logging.info("Adding custom marker 6: Diamond shape, red color, with text below...")
    marker_6 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 8 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 8 // 10]['high'] * 1.02,
        shape=MarkerShape.DIAMOND,
        color=Color.RED,
        size=Size.M,
        text="Text Below",
        text_color='rgba(255, 255, 255, 1)',
        text_size=12,
        text_position='below'
    )
    custom_markers.append(marker_6)

    pause_for_next("Custom marker 6 added.", interactive_mode, delay * 2)
    
    # Custom Marker 7: Circle shape
    logging.info("Adding custom marker 7: Circle shape...")
    marker_7 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 2 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 2 // 10]['high'] * 1.03,
        shape=MarkerShape.CIRCLE,
        color=Color.CYAN,
        size=Size.M,
        text="Circle Marker"
    )
    custom_markers.append(marker_7)

    pause_for_next("Custom marker 7 added.", interactive_mode, delay * 2)
    
    # Custom Marker 8: Square shape
    logging.info("Adding custom marker 8: Square shape...")
    marker_8 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 4 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 4 // 10]['low'] * 0.97,
        shape=MarkerShape.SQUARE,
        color=Color.GOLD,
        size=14,
        text="Square Marker"
    )
    custom_markers.append(marker_8)

    pause_for_next("Custom marker 8 added.", interactive_mode, delay * 2)
    
    # Custom Marker 9: Arrow Up shape
    logging.info("Adding custom marker 9: Arrow Up shape...")
    marker_9 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 6 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 6 // 10]['low'] * 0.96,
        shape=MarkerShape.ARROW_UP,
        color=Color.BRIGHT_GREEN,
        size=Size.M,
        text="Arrow Up"
    )
    custom_markers.append(marker_9)

    pause_for_next("Custom marker 9 added.", interactive_mode, delay * 2)
    
    # Custom Marker 10: Arrow Down shape
    logging.info("Adding custom marker 10: Arrow Down shape...")
    marker_10 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 8 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 8 // 10]['high'] * 1.04,
        shape=MarkerShape.ARROW_DOWN,
        color=Color.BRIGHT_RED,
        size=Size.XXXXL,
        text="Arrow Down",
        text_position=TextPosition.BELOW
    )
    custom_markers.append(marker_10)

    pause_for_next("Custom marker 10 added.", interactive_mode, delay * 2)
    
    # Custom Marker 11: Cross shape
    print("Adding custom marker 11: Cross shape...")
    marker_11 = candlestick_series.add_custom_marker(
        time=candlestick_data[len(candlestick_data) * 8 // 10]['time'],
        price=candlestick_data[len(candlestick_data) * 8 // 10]['high'] * 1.1,
        shape=MarkerShape.CROSS,
        color=Color.BRIGHT_RED,
        size=Size.XL,
        text="CROSS",
        text_position=TextPosition.ABOVE
    )
    custom_markers.append(marker_11)

    pause_for_next("Custom marker 11 added.", interactive_mode, delay * 2)
    
    # Remove custom markers one by one
    for i, marker in enumerate(custom_markers, 1):
        logging.info(f"Removing custom marker {i}...")
        marker.delete()
        logging.info(f"Custom marker {i} removed")
        
        if i < len(custom_markers):  # Don't wait after last removal
            pause_for_next(f"Custom marker {i} removed", interactive_mode, delay * 0.5)
    
    logging.info("Custom marker test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Custom Marker Test - Testing custom marker addition, styling configuration, and deletion functionality")
    
    # Set logging level
    import logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create chart
    chart = create_test_chart(args.host, args.port)
    
    try:
        # Setup test environment
        candlestick_series, volume_series, candlestick_data, volume_data, _ = setup_test_environment(
            chart, args.days
        )
        
        # Run test
        test_custom_marker(candlestick_series, volume_series, candlestick_data, volume_data,
                           args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()