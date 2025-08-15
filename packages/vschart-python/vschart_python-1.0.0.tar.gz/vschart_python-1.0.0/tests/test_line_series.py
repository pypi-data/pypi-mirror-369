#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Line Series Test
Testing line series addition and deletion functionality
"""

import argparse
import time
import logging
from tkinter import W
from typing import List, Dict, Any

from vschart import Chart, CandlestickSeries, LineSeries
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_line_series(candlestick_series, volume_series, 
                    candlestick_data: List[Dict[str, Any]], 
                    volume_data: List[Dict[str, Any]], 
                    delay: float, interactive_mode: bool) -> None:
    """
    Test line series addition and deletion functionality
    
    Args:
        candlestick_series: Candlestick series object
        volume_series: Volume series object
        candlestick_data: Candlestick chart data
        volume_data: Volume chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting line series functionality test...")
    
    # Get chart instance
    chart = candlestick_series.chart
    
    # Create middle line data (average of high and low prices)
    line_data = [{'time': d['time'], 'value': (d['high'] + d['low']) / 2} 
                 for d in candlestick_data]
    
    # Create average volume data (using volume data)
    avg_volume_data = [{'time': d['time'], 'value': d['value']} 
                      for d in volume_data]
    
    # Add line series to pane 0
    logging.info("Adding middle line series to pane 0...")
    line_series = chart.add_line_series(
        pane=0,
        color='rgba(33, 150, 243, 1)',
        line_width=2,
        line_style=0,  # LineStyle.SOLID
        title='Middle Line'
    )
    line_series.set_data(line_data)
    logging.info(f"Line series added, ID: {line_series.id}")
    
    # Add average volume line series to pane 1
    logging.info("Adding average volume line series to pane 1...")
    avg_volume_series = chart.add_line_series(
        pane=1,
        color='rgba(255, 152, 0, 1)',
        line_width=2,
        title="Average Volume"
    )
    avg_volume_series.set_data(avg_volume_data)
    logging.info(f"Average volume line series added, ID: {avg_volume_series.id}")
    
    pause_for_next("Line series added.", interactive_mode, delay)
    
    # Remove middle line series
    logging.info("Removing middle line series...")
    line_series.delete()
    logging.info("Middle line series removed")
    
    pause_for_next("Middle line series removed.", interactive_mode, delay)
    
    # Remove average volume line series
    logging.info("Removing average volume line series...")
    avg_volume_series.delete()
    logging.info("Average volume line series removed")
    
    logging.info("Line series test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Line Series Test - Testing line series addition and deletion")
    
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
        test_line_series(candlestick_series, volume_series, 
                        candlestick_data, volume_data, 
                        args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()