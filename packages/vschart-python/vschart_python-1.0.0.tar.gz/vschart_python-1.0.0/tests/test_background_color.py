#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Background Color Test
Testing background color setting and removal functionality
"""

import argparse
import time
import logging

from typing import List, Dict, Any

from vschart import Chart, CandlestickSeries, BackgroundColor
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_background_color(candlestick_series: CandlestickSeries, volume_series,
                         candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                         delay: float, interactive_mode: bool) -> None:
    """
    Test background color setting and removal functionality
    
    Args:
        candlestick_series: Candlestick series object
        candlestick_data: Candlestick data
        delay: Operation delay between actions
        interactive_mode: Whether in interactive mode
    """
    logging.info("Starting background color functionality test...")
    background_colors = []
    
    # Background color 1: Blue semi-transparent background
    logging.info("Adding background color 1: Blue semi-transparent background...")
    start_index_1 = len(candlestick_data) * 1 // 10
    end_index_1 = len(candlestick_data) * 3 // 10
    
    # Create background color data
    background_data = []
    for i in range(start_index_1, end_index_1 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(33, 150, 243, 0.3)'
        })
    
    bg_1 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_1)
    logging.info(f"Background color 1 added, ID: {bg_1.id}")
    
    # Background color 2: Red semi-transparent background
    logging.info("Adding background color 2: Red semi-transparent background...")
    start_index_2 = len(candlestick_data) * 3 // 10
    end_index_2 = len(candlestick_data) * 5 // 10
    
    background_data = []
    for i in range(start_index_2, end_index_2 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(255, 82, 82, 0.3)'
        })
    
    bg_2 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_2)
    logging.info(f"Background color 2 added, ID: {bg_2.id}")
    
    # Background color 3: Green semi-transparent background
    logging.info("Adding background color 3: Green semi-transparent background...")
    start_index_3 = len(candlestick_data) * 5 // 10
    end_index_3 = len(candlestick_data) * 7 // 10
    
    background_data = []
    for i in range(start_index_3, end_index_3 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(76, 175, 80, 0.3)'
        })
    
    bg_3 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_3)
    logging.info(f"Background color 3 added, ID: {bg_3.id}")
    
    # Background color 4: Purple semi-transparent background
    logging.info("Adding background color 4: Purple semi-transparent background...")
    start_index_4 = len(candlestick_data) * 7 // 10
    end_index_4 = len(candlestick_data) * 9 // 10
    
    background_data = []
    for i in range(start_index_4, end_index_4 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(156, 39, 176, 0.3)'
        })
    
    bg_4 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_4)
    logging.info(f"Background color 4 added, ID: {bg_4.id}")
    
    # Background color 5: Orange semi-transparent background, no text
    logging.info("Adding background color 5: Orange semi-transparent background, no text...")
    start_index_5 = len(candlestick_data) * 2 // 10
    end_index_5 = len(candlestick_data) * 4 // 10
    
    background_data = []
    for i in range(start_index_5, end_index_5 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(255, 140, 0, 0.2)'
        })
    
    bg_5 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_5)
    logging.info(f"Background color 5 added, ID: {bg_5.id}")
    
    # Background color 6: Cyan semi-transparent background
    logging.info("Adding background color 6: Cyan semi-transparent background...")
    start_index_6 = len(candlestick_data) * 6 // 10
    end_index_6 = len(candlestick_data) * 8 // 10
    
    background_data = []
    for i in range(start_index_6, end_index_6 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(0, 188, 212, 0.25)'
        })
    
    bg_6 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_6)
    logging.info(f"Background color 6 added, ID: {bg_6.id}")
    
    # Background color 7: Yellow semi-transparent background
    logging.info("Adding background color 7: Yellow semi-transparent background...")
    start_index_7 = len(candlestick_data) * 8 // 10
    end_index_7 = len(candlestick_data) * 95 // 100
    
    background_data = []
    for i in range(start_index_7, end_index_7 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(255, 193, 7, 0.3)'
        })
    
    bg_7 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_7)
    logging.info(f"Background color 7 added, ID: {bg_7.id}")
    
    # Background color 8: Pink semi-transparent background, no text
    logging.info("Adding background color 8: Pink semi-transparent background, no text...")
    start_index_8 = len(candlestick_data) * 0 // 10
    end_index_8 = len(candlestick_data) * 2 // 10
    
    background_data = []
    for i in range(start_index_8, end_index_8 + 1):
        background_data.append({
            'time': candlestick_data[i]['time'],
            'color': 'rgba(255, 64, 129, 0.2)'
        })
    
    bg_8 = candlestick_series.add_background_color(background_data)
    background_colors.append(bg_8)
    logging.info(f"Background color 8 added, ID: {bg_8.id}")
    
    # Display all background colors
    pause_for_next("All background colors added.", interactive_mode, delay * 2)
    
    # Remove background colors individually
    for i, bg in enumerate(background_colors, 1):
        logging.info(f"Removing background color {i}...")
        bg.delete()
        logging.info(f"Background color {i} removed")
        
        if i < len(background_colors):  # Don't wait after the last one
            pause_for_next(f"Background color {i} removed.", interactive_mode, delay * 0.5)
    
    logging.info("Background color test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Background color test - Testing background color setting and removal functionality")
    
    # Set log level
    import logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create chart
    chart = create_test_chart(args.host, args.port)
    
    try:
        # Set up test environment
        candlestick_series, volume_series, candlestick_data, volume_data, _ = setup_test_environment(
            chart, args.days
        )
        
        # Run test
        test_background_color(candlestick_series, volume_series, candlestick_data, volume_data,
                            args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()