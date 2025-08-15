#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Candlestick Options Test
Testing various candlestick option configuration features
"""

import argparse
import time
import logging
from typing import List, Dict, Any

from vschart import Chart, CandlestickSeries
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_candlestick_options(candlestick_series: CandlestickSeries, volume_series,
                           candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                           delay: float, interactive_mode: bool) -> None:
    """
    Test candlestick options configuration functionality
    
    Args:
        candlestick_series: Candlestick series object
        volume_series: Volume series object
        candlestick_data: Candlestick chart data
        volume_data: Volume chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting candlestick options functionality test...")
    
    # Initial configuration
    logging.info("Setting initial candlestick options...")
    candlestick_series.set_up_color('rgba(0, 200, 0, 1)')
    candlestick_series.set_down_color('rgba(255, 0, 0, 1)')
    candlestick_series.set_wick_visible(True)
    candlestick_series.set_border_visible(True)
    candlestick_series.set_border_color('rgba(255, 255, 255, 1)')
    candlestick_series.set_wick_color('rgba(255, 255, 255, 1)')
    logging.info("Initial candlestick options set")
    
    pause_for_next("Initial configuration applied", interactive_mode, delay)
    
    # Change color scheme to blue
    logging.info("Changing candlestick colors to blue scheme...")
    candlestick_series.set_up_color('rgba(0, 150, 255, 1)')
    candlestick_series.set_down_color('rgba(30, 60, 255, 1)')
    candlestick_series.set_wick_color('rgba(100, 100, 255, 1)')
    candlestick_series.set_border_color('rgba(100, 100, 255, 1)')
    logging.info("Blue color scheme applied")
    
    pause_for_next("Blue color scheme applied.", interactive_mode, delay)
    
    # Change color scheme to orange
    logging.info("Changing candlestick colors to orange scheme...")
    candlestick_series.set_up_color('rgba(255, 140, 0, 1)')
    candlestick_series.set_down_color('rgba(255, 80, 0, 1)')
    candlestick_series.set_wick_color('rgba(255, 160, 0, 1)')
    candlestick_series.set_border_color('rgba(255, 160, 0, 1)')
    logging.info("Orange color scheme applied")
    
    pause_for_next("Orange color scheme applied.", interactive_mode, delay)
    
    # Hide border
    logging.info("Hiding candlestick border...")
    candlestick_series.set_border_visible(False)
    logging.info("Border hidden")
    
    pause_for_next("Border hidden.", interactive_mode, delay)
    
    # Hide wick
    logging.info("Hiding candlestick wick...")
    candlestick_series.set_wick_visible(False)
    logging.info("Wick hidden")
    
    pause_for_next("Wick hidden.", interactive_mode, delay)
    
    # Show border and wick
    logging.info("Showing border and wick...")
    candlestick_series.set_border_visible(True)
    candlestick_series.set_wick_visible(True)
    logging.info("Border and wick shown")
    
    pause_for_next("Border and wick shown.", interactive_mode, delay)
    
    # Change border color
    logging.info("Changing border color...")
    candlestick_series.set_border_color('rgba(255, 255, 0, 1)')
    logging.info("Border color changed")
    
    pause_for_next("Border color changed.", interactive_mode, delay)
    
    # Change wick color
    logging.info("Changing wick color...")
    candlestick_series.set_wick_color('rgba(0, 255, 255, 1)')
    logging.info("Wick color changed")
    
    pause_for_next("Wick color changed.", interactive_mode, delay)
    
    # Restore default configuration
    logging.info("Restoring default candlestick configuration...")
    candlestick_series.set_up_color('rgba(0, 200, 0, 1)')
    candlestick_series.set_down_color('rgba(255, 0, 0, 1)')
    candlestick_series.set_wick_visible(True)
    candlestick_series.set_border_visible(True)
    candlestick_series.set_border_color('rgba(255, 255, 255, 1)')
    candlestick_series.set_wick_color('rgba(255, 255, 255, 1)')
    logging.info("Default configuration restored")
    
    logging.info("Candlestick options test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Candlestick Options Test - Testing various candlestick option configuration features")
    
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
        test_candlestick_options(candlestick_series, volume_series, candlestick_data, volume_data,
                               args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()