#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rectangle Test
Testing rectangle addition, styling configuration, and deletion functionality
"""

import argparse
import time
import logging
from tkinter import W
from typing import List, Dict, Any

from vschart import Chart, CandlestickSeries, Rectangle, VolumeSeries
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_rectangles(candlestick_series: CandlestickSeries, volume_series,
                   candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                   delay: float, interactive_mode: bool) -> None:
    """
    Test rectangle addition, styling configuration, and deletion functionality
    
    Args:
        candlestick_series: Candlestick series object
        volume_series: Volume series object
        candlestick_data: Candlestick chart data
        volume_data: Volume chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting rectangle functionality test...")
    rectangles = []
    
    # Rectangle 1: Solid border, thick width, blue
    logging.info("Adding rectangle 1: Solid border, thick width, blue...")
    start_index_1 = len(candlestick_data) * 1 // 10
    end_index_1 = len(candlestick_data) * 3 // 10
    start_price_1 = candlestick_data[start_index_1]['low'] * 0.98
    end_price_1 = candlestick_data[end_index_1]['high'] * 1.02
    
    rectangle_1 = candlestick_series.add_rectangle(
        start_time=candlestick_data[start_index_1]['time'],
        start_price=start_price_1,
        end_time=candlestick_data[end_index_1]['time'],
        end_price=end_price_1,
        text="Solid Blue",
        border_color='rgba(33, 150, 243, 1)',
        border_width=3,
        line_style='solid',
        fill_color='rgba(33, 150, 243, 0.2)',
        show_text=True,
        text_position='inside',
        text_color='rgba(255, 255, 255, 1)',
        text_background_color='rgba(33, 150, 243, 0.8)',
        text_size=12
    )
    rectangles.append(rectangle_1)
    logging.info(f"Rectangle 1 added, ID: {rectangle_1.id}")
    
    # Rectangle 2: Dashed border, medium width, red
    logging.info("Adding rectangle 2: Dashed border, medium width, red...")
    start_index_2 = len(candlestick_data) * 4 // 10
    end_index_2 = len(candlestick_data) * 6 // 10
    start_price_2 = candlestick_data[start_index_2]['low'] * 1.01
    end_price_2 = candlestick_data[end_index_2]['high'] * 0.99
    
    rectangle_2 = candlestick_series.add_rectangle(
        start_time=candlestick_data[start_index_2]['time'],
        start_price=start_price_2,
        end_time=candlestick_data[end_index_2]['time'],
        end_price=end_price_2,
        text="Dashed Red",
        border_color='rgba(255, 82, 82, 1)',
        border_width=2,
        line_style='dashed',
        fill_color='rgba(255, 82, 82, 0.2)',
        show_text=True,
        text_position='inside',
        text_color='rgba(255, 82, 82, 1)',
        text_background_color='rgba(255, 255, 255, 0.9)',
        text_size=14
    )
    rectangles.append(rectangle_2)
    logging.info(f"Rectangle 2 added, ID: {rectangle_2.id}")
    
    # Rectangle 3: Dotted border, thin width, green
    logging.info("Adding rectangle 3: Dotted border, thin width, green...")
    start_index_3 = len(candlestick_data) * 7 // 10
    end_index_3 = len(candlestick_data) * 9 // 10
    start_price_3 = candlestick_data[start_index_3]['low'] * 0.995
    end_price_3 = candlestick_data[end_index_3]['high'] * 1.005
    
    rectangle_3 = candlestick_series.add_rectangle(
        start_time=candlestick_data[start_index_3]['time'],
        start_price=start_price_3,
        end_time=candlestick_data[end_index_3]['time'],
        end_price=end_price_3,
        text="Dotted Green",
        border_color='rgba(76, 175, 80, 1)',
        border_width=1,
        line_style='dotted',
        fill_color='rgba(76, 175, 80, 0.2)',
        show_text=True,
        text_position='inside',
        text_color='rgba(76, 175, 80, 1)',
        text_background_color='rgba(255, 255, 255, 0.7)',
        text_size=10
    )
    rectangles.append(rectangle_3)
    logging.info(f"Rectangle 3 added, ID: {rectangle_3.id}")
    
    # Rectangle 4: Large dashed border, purple, no background fill
    logging.info("Adding rectangle 4: Large dashed border, purple, no background fill...")
    start_index_4 = len(candlestick_data) * 2 // 10
    end_index_4 = len(candlestick_data) * 8 // 10
    start_price_4 = candlestick_data[start_index_4]['high'] * 1.03
    end_price_4 = candlestick_data[end_index_4]['high'] * 1.06
    
    rectangle_4 = candlestick_series.add_rectangle(
        start_time=candlestick_data[start_index_4]['time'],
        start_price=start_price_4,
        end_time=candlestick_data[end_index_4]['time'],
        end_price=end_price_4,
        text="Purple Border",
        border_color='rgba(156, 39, 176, 1)',
        border_width=4,
        line_style='large_dashed',
        fill_color='transparent',
        show_text=True,
        text_position='inside',
        text_color='rgba(156, 39, 176, 1)',
        text_background_color='rgba(255, 255, 255, 0.95)',
        text_size=16
    )
    rectangles.append(rectangle_4)
    logging.info(f"Rectangle 4 added, ID: {rectangle_4.id}")
    
    # Rectangle 5: Sparse dotted border, orange, semi-transparent fill
    logging.info("Adding rectangle 5: Sparse dotted border, orange, semi-transparent fill...")
    start_index_5 = len(candlestick_data) * 1 // 10
    end_index_5 = len(candlestick_data) * 5 // 10
    start_price_5 = candlestick_data[start_index_5]['low'] * 0.96
    end_price_5 = candlestick_data[end_index_5]['low'] * 0.98
    
    rectangle_5 = candlestick_series.add_rectangle(
        start_time=candlestick_data[start_index_5]['time'],
        start_price=start_price_5,
        end_time=candlestick_data[end_index_5]['time'],
        end_price=end_price_5,
        text="Orange Sparse",
        border_color='rgba(255, 140, 0, 1)',
        border_width=2,
        line_style='sparse_dotted',
        fill_color='rgba(255, 140, 0, 0.2)',
        show_text=True,
        text_position='inside',
        text_color='rgba(255, 140, 0, 1)',
        text_background_color='rgba(255, 255, 255, 0.8)',
        text_size=13
    )
    rectangles.append(rectangle_5)
    logging.info(f"Rectangle 5 added, ID: {rectangle_5.id}")
    
    # Rectangle 6: No border text, solid border, cyan, light fill
    logging.info("Adding rectangle 6: No border text, solid border, cyan, light fill...")
    start_index_6 = len(candlestick_data) * 6 // 10
    end_index_6 = len(candlestick_data) * 9 // 10
    start_price_6 = candlestick_data[start_index_6]['high'] * 0.995
    end_price_6 = candlestick_data[end_index_6]['high'] * 1.015
    
    rectangle_6 = candlestick_series.add_rectangle(
        start_time=candlestick_data[start_index_6]['time'],
        start_price=end_price_6,
        end_time=candlestick_data[end_index_6]['time'],
        end_price=start_price_6,
        border_color='rgba(0, 188, 212, 1)',
        border_width=2,
        line_style='solid',
        fill_color='rgba(0, 188, 212, 0.2)',
        show_text=False  # Don't show text
    )
    rectangles.append(rectangle_6)
    logging.info(f"Rectangle 6 added, ID: {rectangle_6.id}")
    
    # Display all rectangles
    pause_for_next("All rectangles added.", interactive_mode, delay * 2)
    
    # Remove rectangles one by one
    for i, rectangle in enumerate(rectangles, 1):
        logging.info(f"Removing rectangle {i}...")
        rectangle.delete()
        logging.info(f"Rectangle {i} removed")
        
        if i < len(rectangles):  # Don't wait after last removal
            pause_for_next(f"Rectangle {i} removed.", interactive_mode, delay * 0.5)
    
    logging.info("Rectangle test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Rectangle Test - Testing rectangle addition, styling configuration, and deletion functionality")
    
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
        test_rectangles(candlestick_series, volume_series, candlestick_data, volume_data,
                       args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()