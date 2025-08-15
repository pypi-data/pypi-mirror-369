#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Markers Test
Testing volume marker addition, styling configuration, and deletion functionality
"""

import time
import logging
from typing import List, Dict, Any

from vschart import VolumeSeries, CandlestickSeries
from vschart.constants import MarkerPosition, MarkerShape
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_volume_markers(candlestick_series: CandlestickSeries, volume_series,
                       candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                       delay: float, interactive_mode: bool) -> None:
    """
    Test volume marker addition, styling configuration, and deletion functionality
    
    Args:
        volume_series: Volume series object
        volume_data: Volume data
        delay: Operation delay between actions
        interactive_mode: Whether in interactive mode
    """
    logging.info("Starting volume markers functionality test...")
    markers = []
    
    # Marker 1: Up arrow, green, large marker
    logging.info("Adding volume marker 1: Up arrow, green, large marker...")
    marker_1 = volume_series.add_marker(
        time=volume_data[len(volume_data) * 1 // 10]['time'],
        position=MarkerPosition.BELOW_BAR,
        shape=MarkerShape.ARROW_UP,
        color='rgba(76, 175, 80, 1)',
        size=2,
        text="Volume surge up"
    )
    markers.append(marker_1)
    logging.info(f"Volume marker 1 added, ID: {marker_1.id}")
    
    # Marker 2: Down arrow, red, medium marker
    logging.info("Adding volume marker 2: Down arrow, red, medium marker...")
    marker_2 = volume_series.add_marker(
        time=volume_data[len(volume_data) * 3 // 10]['time'],
        position=MarkerPosition.ABOVE_BAR,
        shape=MarkerShape.ARROW_DOWN,
        color='rgba(255, 82, 82, 1)',
        size=1,
        text="Volume decline down"
    )
    markers.append(marker_2)
    logging.info(f"Volume marker 2 added, ID: {marker_2.id}")
    
    # Marker 3: Circle, blue, small marker
    logging.info("Adding volume marker 3: Circle, blue, small marker...")
    marker_3 = volume_series.add_marker(
        time=volume_data[len(volume_data) * 5 // 10]['time'],
        position=MarkerPosition.ABOVE_BAR,
        shape=MarkerShape.CIRCLE,
        color='rgba(33, 150, 243, 1)',
        size=1,
        text="Extreme volume"
    )
    markers.append(marker_3)
    logging.info(f"Volume marker 3 added, ID: {marker_3.id}")
    
    # Marker 4: Square, orange, medium marker
    logging.info("Adding volume marker 4: Square, orange, medium marker...")
    marker_4 = volume_series.add_marker(
        time=volume_data[len(volume_data) * 7 // 10]['time'],
        position=MarkerPosition.ABOVE_BAR,
        shape=MarkerShape.SQUARE,
        color='rgba(255, 140, 0, 1)',
        size=2,
        text="Low volume"
    )
    markers.append(marker_4)
    logging.info(f"Volume marker 4 added, ID: {marker_4.id}")
    
    # Display all markers
    pause_for_next("Volume markers added", interactive_mode, delay)
    
    # Remove markers individually
    for i, marker in enumerate(markers, 1):
        logging.info(f"Removing volume marker {i}...")
        marker.delete()
        logging.info(f"Volume marker {i} removed")
        
        if i < len(markers):  # Don't wait after last removal
            pause_for_next(f"Volume marker {i} removed.", interactive_mode, delay * 0.5)
    
    logging.info("Volume markers test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Volume markers test - Testing volume marker addition, styling configuration, and deletion functionality")
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create chart
    chart = create_test_chart(args.host, args.port)
    
    try:
        # Set up test environment
        candlestick_series, volume_series, candlestick_data, volume_data, _ = setup_test_environment(
            chart, args.days
        )
        
        # Run test
        test_volume_markers(candlestick_series, volume_series, candlestick_data, volume_data,
                           args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()