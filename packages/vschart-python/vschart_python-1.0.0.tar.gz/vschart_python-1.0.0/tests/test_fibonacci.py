#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fibonacci Retracement Test
Testing Fibonacci retracement addition, configuration, and deletion functionality
"""

import argparse
import time
import logging
from typing import List, Dict, Any

from vschart import Chart, CandlestickSeries, Fibonacci, VolumeSeries
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_fibonacci(candlestick_series: CandlestickSeries, volume_series,
                  candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                  delay: float, interactive_mode: bool) -> None:
    """
    Test Fibonacci retracement functionality
    
    Args:
        candlestick_series: Candlestick series object
        candlestick_data: Candlestick chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting Fibonacci retracement functionality test...")
    
    # Add Fibonacci retracement from 30% to 70% of data
    start_index = len(candlestick_data) * 3 // 10
    end_index = len(candlestick_data) * 7 // 10
    
    logging.info("Adding Fibonacci retracement...")
    fibonacci = candlestick_series.add_fibonacci(
        start_time=candlestick_data[start_index]['time'],
        start_price=candlestick_data[start_index]['high'],
        end_time=candlestick_data[end_index]['time'],
        end_price=candlestick_data[end_index]['low'],
        trend_line_color='rgba(255, 0, 0, 1)',
        trend_line_width=5,
        fib_colors=['rgba(255, 0, 0, 1)', 'rgba(255, 165, 0, 1)', 
                   'rgba(255, 255, 0, 1)', 'rgba(0, 255, 0, 1)', 'rgba(0, 0, 255, 1)'],
        fib_line_width=2,
        fill_colors=[
            'rgba(255, 0, 0, 0.15)',
            'rgba(255, 165, 0, 0.15)',
            'rgba(255, 255, 0, 0.15)',
            'rgba(0, 255, 0, 0.15)',
            'rgba(0, 0, 255, 0.15)'
        ],
        show_fill=True,
        fill_opacity=0.15,
        coefficients=[0, 0.382, 0.618, 1, 1.618],
        extension_bars=10,
        show_labels=True,
        label_background_color='rgba(255, 255, 255, 0.9)',
        label_text_color='rgba(0, 0, 0, 1)',
        label_font_size=14,
        label_position='left'
    )
    
    logging.info(f"Fibonacci retracement added, ID: {fibonacci.id}")
    
    pause_for_next("Fibonacci retracement added.", interactive_mode, delay)
    
    # Test dynamic option changes
    logging.info("Testing dynamic option changes...")
    
    # Change label position to right
    logging.info("Changing label position to right...")
    fibonacci.set_label_position('right')
    pause_for_next("Label position updated.", interactive_mode, delay)
    
    # Increase label font size
    logging.info("Increasing label font size to 16...")
    fibonacci.set_label_font_size(16)
    pause_for_next("Label font size updated.", interactive_mode, delay)
    
    # Hide fill area
    logging.info("Hiding fill area...")
    fibonacci.set_show_fill(False)
    pause_for_next("Fill area hidden.", interactive_mode, delay)
    
    # Show fill area
    logging.info("Showing fill area...")
    fibonacci.set_show_fill(True)
    pause_for_next("Fill area shown.", interactive_mode, delay)
    
    # Reduce fill opacity
    logging.info("Reducing fill opacity to 0.05...")
    fibonacci.set_fill_opacity(0.05)
    pause_for_next("Fill opacity updated.", interactive_mode, delay)
    
    # Reset label position to left
    logging.info("Resetting label position to left...")
    fibonacci.set_label_position('left')
    pause_for_next("Label position reset.", interactive_mode, delay)
    
    # Remove Fibonacci retracement
    logging.info("Removing Fibonacci retracement...")
    fibonacci.delete()
    logging.info("Fibonacci retracement removed")
    
    logging.info("Fibonacci retracement test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Fibonacci retracement test - Testing Fibonacci retracement addition, configuration, and deletion functionality")
    
    # Set log level
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
        test_fibonacci(candlestick_series, volume_series, candlestick_data, volume_data,
                      args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()