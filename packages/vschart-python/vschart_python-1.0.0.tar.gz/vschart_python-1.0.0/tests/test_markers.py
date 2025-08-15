#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marker Test
Testing marker addition, styling configuration, and deletion functionality
"""

import argparse
import time
import logging
from typing import List, Dict, Any

from vschart import CandlestickSeries
from vschart.constants import MarkerPosition, MarkerShape

from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_markers(candlestick_series: CandlestickSeries, volume_series,
                candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                delay: float, interactive_mode: bool) -> None:
    """
    Test marker addition, styling configuration, and deletion functionality
    
    Args:
        candlestick_series: Candlestick series object
        volume_series: Volume series object
        candlestick_data: Candlestick chart data
        volume_data: Volume chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting marker functionality test...")
    markers = []
    
    # Marker 1: Up arrow, green, large marker
    logging.info("Adding marker 1: Up arrow, green, large marker...")
    marker_1 = candlestick_series.add_marker(
        time=candlestick_data[len(candlestick_data) * 1 // 10]['time'],
        position=MarkerPosition.ABOVE_BAR,
        shape=MarkerShape.ARROW_UP,
        color='rgba(76, 175, 80, 1)',
        size=20,
        text="Upward Breakout"
    )
    markers.append(marker_1)
    logging.info(f"Marker 1 added, ID: {marker_1.id}")
    
    # Marker 2: Down arrow, red, medium marker
    logging.info("Adding marker 2: Down arrow, red, medium marker...")
    marker_2 = candlestick_series.add_marker(
        time=candlestick_data[len(candlestick_data) * 3 // 10]['time'],
        position=MarkerPosition.BELOW_BAR,
        shape=MarkerShape.ARROW_DOWN,
        color='rgba(255, 82, 82, 1)',
        size=15,
        text="Downward Breakout"
    )
    markers.append(marker_2)
    logging.info(f"Marker 2 added, ID: {marker_2.id}")
    
    # Marker 3: Circle, blue, small marker
    logging.info("Adding marker 3: Circle, blue, small marker...")
    marker_3 = candlestick_series.add_marker(
        time=candlestick_data[len(candlestick_data) * 5 // 10]['time'],
        position=MarkerPosition.BELOW_BAR,
        shape=MarkerShape.CIRCLE,
        color='rgba(33, 150, 243, 1)',
        size=10,
        text="Support Point"
    )
    markers.append(marker_3)
    logging.info(f"Marker 3 added, ID: {marker_3.id}")
    
    # Marker 4: Square, orange, medium marker
    logging.info("Adding marker 4: Square, orange, medium marker...")
    marker_4 = candlestick_series.add_marker(
        time=candlestick_data[len(candlestick_data) * 7 // 10]['time'],
        position=MarkerPosition.BELOW_BAR,
        shape=MarkerShape.SQUARE,
        color='rgba(255, 140, 0, 1)',
        size=12,
        text="Resistance Point"
    )
    markers.append(marker_4)
    logging.info(f"Marker 4 added, ID: {marker_4.id}")
    
    # Display all markers
    pause_for_next("All markers added.", interactive_mode, delay * 2)
    
    # Remove markers one by one
    for i, marker in enumerate(markers, 1):
        logging.info(f"Removing marker {i}...")
        marker.delete()
        logging.info(f"Marker {i} removed")
        
        if i < len(markers):  # Don't wait after last removal
            pause_for_next(f"Marker {i} removed.", interactive_mode, delay * 0.5)
    
    logging.info("Marker test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Marker Test - Testing marker addition, styling configuration, and deletion functionality")
    
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
        test_markers(candlestick_series, volume_series, candlestick_data, volume_data,
                    args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()