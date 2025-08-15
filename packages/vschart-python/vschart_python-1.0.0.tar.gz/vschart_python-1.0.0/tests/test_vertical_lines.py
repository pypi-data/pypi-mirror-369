#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vertical Lines Test
Testing vertical line addition, styling configuration, and deletion functionality
"""

import argparse
import time
import logging
from typing import List, Dict, Any

from vschart import Chart, CandlestickSeries, VerticalLine
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_vertical_lines(candlestick_series: CandlestickSeries, volume_series,
                       candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                       delay: float, interactive_mode: bool) -> None:
    """
    Test vertical line addition, styling configuration, and deletion functionality
    
    Args:
        candlestick_series: Candlestick series object
        candlestick_data: Candlestick chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting vertical lines functionality test...")
    vertical_lines = []
    
# Vertical line 1: Solid, thick width, blue
    logging.info("Adding vertical line 1: Solid, thick width, blue...")
    line_1 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 1 // 10]['time'],
        label_text="Important Time Point 1",
        color='rgba(33, 150, 243, 1)',
        width=3,
        show_label=True
    )
    vertical_lines.append(line_1)
    logging.info(f"Vertical line 1 added, ID: {line_1.id}")
    
    # Vertical line 2: Dashed, medium width, red
    logging.info("Adding vertical line 2: Dashed, medium width, red...")
    line_2 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 3 // 10]['time'],
        label_text="Important Time Point 2",
        color='rgba(255, 82, 82, 1)',
        width=2,
        show_label=True
    )
    vertical_lines.append(line_2)
    logging.info(f"Vertical line 2 added, ID: {line_2.id}")
    
    # Vertical line 3: Dotted, thin width, green
    logging.info("Adding vertical line 3: Dotted, thin width, green...")
    line_3 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 5 // 10]['time'],
        label_text="Important Time Point 3",
        color='rgba(76, 175, 80, 1)',
        width=1,
        show_label=True
    )
    vertical_lines.append(line_3)
    logging.info(f"Vertical line 3 added, ID: {line_3.id}")

    # Vertical line 4: Large dashed, large width, purple
    logging.info("Adding vertical line 4: Large dashed, large width, purple...")
    line_4 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 7 // 10]['time'],
        label_text="Important Time Point 4",
        color='rgba(156, 39, 176, 1)',
        width=4,
        show_label=True
    )
    vertical_lines.append(line_4)
    logging.info(f"Vertical line 4 added, ID: {line_4.id}")

    # Vertical line 5: Sparse dotted, medium width, orange
    logging.info("Adding vertical line 5: Sparse dotted, medium width, orange...")
    line_5 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 9 // 10]['time'],
        label_text="Important Time Point 5",
        color='rgba(255, 140, 0, 1)',
        width=2,
        show_label=True
    )
    vertical_lines.append(line_5)
    logging.info(f"Vertical line 5 added, ID: {line_5.id}")

    # Vertical line 6: Solid, medium width, cyan, no text
    logging.info("Adding vertical line 6: Solid, medium width, cyan, no text...")
    line_6 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 2 // 10]['time'],
        color='rgba(0, 188, 212, 1)',
        width=2,
        show_label=False
    )
    vertical_lines.append(line_6)
    logging.info(f"Vertical line 6 added, ID: {line_6.id}")

    # Vertical line 7: Dashed, thin width, gray
    logging.info("Adding vertical line 7: Dashed, thin width, gray...")
    line_7 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 4 // 10]['time'],
        label_text="Gray dashed line",
        color='rgba(158, 158, 158, 1)',
        width=1,
        show_label=True
    )
    vertical_lines.append(line_7)
    logging.info(f"Vertical line 7 added, ID: {line_7.id}")

    # Vertical line 8: Dotted, thick width, pink
    logging.info("Adding vertical line 8: Dotted, thick width, pink...")
    line_8 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 6 // 10]['time'],
        label_text="Pink dotted line",
        color='rgba(255, 64, 129, 1)',
        width=3,
        show_label=True
    )
    vertical_lines.append(line_8)
    logging.info(f"Vertical line 8 added, ID: {line_8.id}")

    # Vertical line 9: Solid, thin width, yellow
    logging.info("Adding vertical line 9: Solid, thin width, yellow...")
    line_9 = candlestick_series.add_vertical_line(
        time=candlestick_data[len(candlestick_data) * 8 // 10]['time'],
        label_text="Yellow solid line",
        color='rgba(255, 193, 7, 1)',
        width=1,
        show_label=True
    )
    vertical_lines.append(line_9)
    logging.info(f"Vertical line 9 added, ID: {line_9.id}")
    
    # Display all vertical lines
    pause_for_next("All vertical lines added.", interactive_mode, delay * 2)
    
    # Remove vertical lines one by one
    for i, line in enumerate(vertical_lines, 1):
        logging.info(f"Removing vertical line {i}...")
        line.delete()
        logging.info(f"Vertical line {i} removed")
        
        if i < len(vertical_lines):  # Don't wait after removing the last one
            pause_for_next(f"Vertical line {i} removed.", interactive_mode, delay * 0.5)
    
    logging.info("Vertical lines test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Vertical lines test - Testing vertical line addition, styling configuration, and deletion functionality")
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create chart
    chart = create_test_chart(args.host, args.port)
    
    try:
        # Setup test environment
        candlestick_series, volume_series, candlestick_data, volume_data, _ = setup_test_environment(
            chart, args.days
        )
        # Run test
        test_vertical_lines(candlestick_series, volume_series, candlestick_data, volume_data,
                          args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()