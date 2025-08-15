#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Line Options Test
Testing various line option configurations
"""

import argparse
import time
import logging
from typing import List, Dict, Any

from vschart import Chart, LineSeries
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_line_options(candlestick_series, volume_series, 
                     candlestick_data: List[Dict[str, Any]], 
                     volume_data: List[Dict[str, Any]], 
                     delay: float, interactive_mode: bool) -> None:
    """
    Test line options configuration functionality
    
    Args:
        candlestick_series: Candlestick series object
        volume_series: Volume series object
        candlestick_data: Candlestick chart data
        volume_data: Volume chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting line options functionality test...")
    
    # Get chart instance
    chart = candlestick_series.chart
    
    # Create line data (using median of candlestick data)
    line_data = [{'time': d['time'], 'value': (d['high'] + d['low']) / 2} 
                 for d in candlestick_data]
    
    # Create line series
    line_series = chart.add_line_series(
        pane=0,
        color='#2196f3',
        line_width=2,
        line_style=0,
        title='Test Line'
    )
    line_series.set_data(line_data)
    
    # Initial configuration
    logging.info("Setting initial line options...")
    line_series.set_color('#2196f3')
    line_series.set_line_width(2)
    line_series.set_line_style(0)
    line_series.set_last_value_visible(True)
    line_series.set_price_line_visible(True)
    line_series.set_price_line_width(1)
    line_series.set_price_line_color('#2196f3')
    line_series.set_price_line_style(2)
    line_series.set_point_markers_visible(False)
    line_series.set_title('Price Line')
    logging.info("Initial line options set")
    
    pause_for_next("Initial configuration applied", interactive_mode, delay)
    
    # Change line color
    logging.info("Changing line color to red...")
    line_series.set_color('#f44336')
    line_series.set_price_line_color('#f44336')
    logging.info("Red line applied")
    
    pause_for_next("Red line applied", interactive_mode, delay)
    
    # Change line width
    logging.info("Changing line width to thick...")
    line_series.set_line_width(4)
    line_series.set_price_line_width(2)
    logging.info("Thick line applied")
    
    pause_for_next("Thick line applied", interactive_mode, delay)
    
    # Change line style
    logging.info("Changing line style to dashed...")
    line_series.set_line_style(1)
    line_series.set_price_line_style(1)
    logging.info("Dashed line applied")
    
    pause_for_next("Dashed line applied", interactive_mode, delay)
    
    # Change line style to dotted
    logging.info("Changing line style to dotted...")
    line_series.set_line_style(2)
    line_series.set_price_line_style(2)
    logging.info("Dotted line applied")
    
    pause_for_next("Dotted line applied", interactive_mode, delay)
    
    # Hide price line
    logging.info("Hiding price line...")
    line_series.set_price_line_visible(False)
    logging.info("Price line hidden")
    
    pause_for_next("Price line hidden", interactive_mode, delay)
    
    # Show price line
    logging.info("Showing price line...")
    line_series.set_price_line_visible(True)
    logging.info("Price line shown")
    
    pause_for_next("Price line shown", interactive_mode, delay)
    
    # Hide last value
    logging.info("Hiding last value...")
    line_series.set_last_value_visible(False)
    logging.info("Last value hidden")
    
    pause_for_next("Last value hidden", interactive_mode, delay)
    
    # Show last value
    logging.info("Showing last value...")
    line_series.set_last_value_visible(True)
    logging.info("Last value shown")
    
    pause_for_next("Last value shown", interactive_mode, delay)
    
    # Modify title
    logging.info("Modifying line title...")
    line_series.set_title('Test Line')
    logging.info("Title modified")
    
    pause_for_next("Title modified", interactive_mode, delay)
    
    # Restore default configuration
    logging.info("Restoring default line configuration...")
    line_series.set_color('#2196f3')
    line_series.set_line_width(2)
    line_series.set_line_style(0)
    line_series.set_last_value_visible(True)
    line_series.set_price_line_visible(True)
    line_series.set_price_line_color('#2196f3')
    line_series.set_price_line_width(1)
    line_series.set_price_line_style(2)
    line_series.set_title('Price Line')
    logging.info("Default configuration restored")
    
    logging.info("Line options test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Line options test - Testing various line option configurations")
    
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
        test_line_options(candlestick_series, volume_series, candlestick_data, volume_data,
                          args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()