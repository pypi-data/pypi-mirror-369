#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trend lines test
Testing various trend line options and configurations
"""

import time
import logging

from typing import List, Dict, Any

from vschart import CandlestickSeries, VolumeSeries
from vschart.constants import LineStyle
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_trend_lines(candlestick_series: CandlestickSeries,
                     volume_series: VolumeSeries,
                     candlestick_data: List[Dict[str, Any]], 
                     volume_data: List[Dict[str, Any]], 
                     delay: float, interactive_mode: bool) -> None:
    """
    Test trend line creation with various options and configurations
    
    Args:
        candlestick_series: Candlestick series object
        volume_series: Volume series object
        candlestick_data: Candlestick chart data
        volume_data: Volume chart data
        delay: Operation delay between actions
        interactive_mode: Whether to run in interactive mode
    """
    logging.info("Starting trend lines functionality test...")
    # Get chart instance
    chart = candlestick_series.chart
    
    # Test 1: Basic trend line with default options
    logging.info("\n=== Test 1: Basic trend line ===")
    start_idx = len(candlestick_data) // 5
    end_idx = len(candlestick_data) * 4 // 5
    
    trend_line1 = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['low'] * 0.98,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['high'] * 1.02,
        line_color='rgba(255, 0, 0, 1)',
        line_style=LineStyle.SOLID,
        width=2,
        show_labels=True
    )
    logging.info(f"Basic trend line added, ID: {trend_line1.id}")
    
    pause_for_next("Basic trend line added.", interactive_mode, delay)
    
    # Test 2: Thick green trend line with custom line style
    logging.info("\n=== Test 2: Thick green trend line ===")
    trend_line2 = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx * 2]['high'] * 1.02,
        end_time=candlestick_data[end_idx // 2]['time'],
        end_price=candlestick_data[end_idx // 2]['low'] * 0.98,
        line_color='rgba(0, 255, 0, 0.8)',
        line_style=LineStyle.SOLID,
        width=4,
        show_labels=True,
        label_text_color='rgba(0, 255, 0, 1)'
    )
    logging.info(f"Green trend line added, ID: {trend_line2.id}")
    
    pause_for_next("Green trend line added.", interactive_mode, delay)
    
    # Test 3: Dashed blue trend line without labels
    logging.info("\n=== Test 3: Blue dashed trend line ===")
    trend_line3 = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx // 2]['time'],
        start_price=candlestick_data[start_idx // 2]['close'],
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['close'],
        line_color='rgba(0, 100, 255, 0.7)',
        width=1,
        line_style=LineStyle.DASHED,
        show_labels=False
    )
    logging.info(f"Blue dashed trend line added, ID: {trend_line3.id}")
    
    pause_for_next("Blue trend line added.", interactive_mode, delay)
    
    # Test 4: Dotted purple trend line with extended lines
    logging.info("\n=== Test 4: Purple dotted trend line ===")
    trend_line4 = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx * 3]['time'],
        start_price=candlestick_data[start_idx * 3]['low'],
        end_time=candlestick_data[end_idx * 3 // 4]['time'],
        end_price=candlestick_data[end_idx * 3 // 4]['high'],
        line_color='rgba(128, 0, 128, 0.9)',
        width=3,
        line_style=LineStyle.DOTTED,
        show_labels=True
    )
    logging.info(f"Purple dotted trend line added, ID: {trend_line4.id}")
    
    pause_for_next("Purple dotted trend line added.", interactive_mode, delay)
    
    # Test 5: Update existing trend line properties
    logging.info("\n=== Test 5: Updating trend line properties ===")
    trend_line1.set_line_color('rgba(255, 165, 0, 1)')
    trend_line1.set_width(5)
    trend_line1.set_line_style(LineStyle.LARGE_DASHED)
    logging.info("Trend line 1 updated to orange thick dashed line")
    
    pause_for_next("Trend line updated.", interactive_mode, delay)
    
    # Test 6: Trend line on volume series
    logging.info("\n=== Test 6: Trend line on volume series ===")
    volume_trend_line = volume_series.add_trend_line(
        start_time=volume_data[start_idx]['time'],
        start_price=volume_data[start_idx]['value'] * 0.8,
        end_time=volume_data[end_idx]['time'],
        end_price=volume_data[end_idx]['value'] * 1.2,
        line_color='rgba(255, 140, 0, 0.8)',
        line_style=LineStyle.SOLID,
        width=2,
        show_labels=True
    )
    logging.info(f"Volume trend line added, ID: {volume_trend_line.id}")
    
    pause_for_next("Volume trend line added.", interactive_mode, delay)

    # Test 7: Multiple parallel trend lines (channel)
    logging.info("\n=== Test 7: Trend channel with parallel lines ===")
    channel_top = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['high'] * 1.05,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['high'] * 1.05,
        line_color='rgba(0, 255, 255, 0.7)',
        line_style=LineStyle.SOLID,
        width=1,
        show_labels=True
    )
    
    channel_bottom = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['low'] * 0.95,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['low'] * 0.95,
        line_color='rgba(0, 255, 255, 0.7)',
        line_style=LineStyle.SOLID,
        width=1,
        show_labels=True
    )
    logging.info(f"Trend channel added - Top ID: {channel_top.id}, Bottom ID: {channel_bottom.id}")
    
    pause_for_next("Trend channel added.", interactive_mode, delay)

    # Test 8: Horizontal trend lines (support/resistance levels)
    logging.info("\n=== Test 8: Horizontal support/resistance levels ===")
    resistance_level = candlestick_series.add_trend_line(
        start_time=candlestick_data[0]['time'],
        start_price=max(d['high'] for d in candlestick_data) * 0.98,
        end_time=candlestick_data[-1]['time'],
        end_price=max(d['high'] for d in candlestick_data) * 0.98,
        line_color='rgba(255, 0, 0, 0.8)',
        line_style=LineStyle.SOLID,
        width=2,
        show_labels=True
    )
    
    support_level = candlestick_series.add_trend_line(
        start_time=candlestick_data[0]['time'],
        start_price=min(d['low'] for d in candlestick_data) * 1.02,
        end_time=candlestick_data[-1]['time'],
        end_price=min(d['low'] for d in candlestick_data) * 1.02,
        line_color='rgba(0, 128, 0, 0.8)',
        line_style=LineStyle.SOLID,
        width=2,
        show_labels=True
    )
    logging.info(f"Support/resistance levels added - Resistance ID: {resistance_level.id}, Support ID: {support_level.id}")
    
    pause_for_next("Support/resistance levels added.", interactive_mode, delay)

    # Test 10: Trend lines with different line styles
    logging.info("\n=== Test 10: Trend lines with different line styles ===")
    
    # Solid line (default)
    solid_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['low'] * 0.99,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['low'] * 0.99,
        line_color='rgba(0, 0, 0, 1)',
        width=2,
        line_style=LineStyle.SOLID,
        show_labels=True
    )
    
    # Dotted line
    dotted_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['low'] * 0.98,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['low'] * 0.98,
        line_color='rgba(255, 0, 0, 1)',
        width=2,
        line_style=LineStyle.DOTTED,
        show_labels=True
    )
    
    # Dashed line
    dashed_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['low'] * 0.97,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['low'] * 0.97,
        line_color='rgba(0, 255, 0, 1)',
        width=2,
        line_style=LineStyle.DASHED,
        show_labels=True
    )
    
    # Large dashed line
    large_dashed_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['low'] * 0.96,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['low'] * 0.96,
        line_color='rgba(0, 0, 255, 1)',
        width=2,
        line_style=LineStyle.LARGE_DASHED,
        show_labels=True
    )
    
    # Sparse dotted line
    sparse_dotted_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['low'] * 0.95,
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['low'] * 0.95,
        line_color='rgba(128, 0, 128, 1)',
        width=2,
        line_style=LineStyle.SPARSE_DOTTED,
        show_labels=True
    )
    
    logging.info(f"All line styles added - IDs: {solid_line.id}, {dotted_line.id}, {dashed_line.id}, {large_dashed_line.id}, {sparse_dotted_line.id}")
    
    pause_for_next("All line styles added.", interactive_mode, delay)

    # Test 9: Trend line with custom label positioning
    logging.info("\n=== Test 9: Trend line with custom label positioning ===")
    custom_label_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx * 2]['time'],
        start_price=candlestick_data[start_idx * 2]['close'] * 1.01,
        end_time=candlestick_data[end_idx * 3 // 4]['time'],
        end_price=candlestick_data[end_idx * 3 // 4]['close'] * 0.99,
        line_color='rgba(255, 20, 147, 0.9)',
        width=3,
        line_style=LineStyle.SOLID,
        show_labels=True,
        label_text_color='rgba(255, 20, 147, 1)'
    )
    logging.info(f"Custom label trend line added, ID: {custom_label_line.id}")
    
    pause_for_next("Custom label trend line added.", interactive_mode, delay)

    # Test 10: Trend line with opacity variations
    logging.info("\n=== Test 10: Trend lines with different opacity levels ===")
    transparent_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx // 2]['time'],
        start_price=candlestick_data[start_idx // 2]['high'] * 1.03,
        end_time=candlestick_data[end_idx * 4 // 5]['time'],
        end_price=candlestick_data[end_idx * 4 // 5]['high'] * 1.03,
        line_color='rgba(75, 0, 130, 0.3)',
        line_style=LineStyle.SOLID,
        width=4,
        show_labels=True
    )
    
    semi_transparent_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx * 3]['time'],
        start_price=candlestick_data[start_idx * 3]['low'] * 0.97,
        end_time=candlestick_data[end_idx * 2 // 3]['time'],
        end_price=candlestick_data[end_idx * 2 // 3]['low'] * 0.97,
        line_color='rgba(220, 20, 60, 0.6)',
        line_style=LineStyle.SOLID,
        width=2,
        show_labels=True
    )
    logging.info(f"Opacity variation trend lines added - Transparent ID: {transparent_line.id}, Semi-transparent ID: {semi_transparent_line.id}")
    
    pause_for_next("Opacity variation trend lines added.", interactive_mode, delay)

    # Test 11: Dynamic trend line updates
    logging.info("\n=== Test 11: Dynamic trend line updates ===")
    dynamic_line = candlestick_series.add_trend_line(
        start_time=candlestick_data[start_idx]['time'],
        start_price=candlestick_data[start_idx]['close'],
        end_time=candlestick_data[end_idx]['time'],
        end_price=candlestick_data[end_idx]['close'],
        line_color='rgba(0, 0, 0, 0.8)',
        line_style=LineStyle.SOLID,
        width=2,
        show_labels=True
    )
    
    # Update the line multiple times with different properties
    for i in range(3):
        new_color = f'rgba({i*80}, {100+i*50}, {200-i*30}, 0.8)'
        new_width = 2 + i
        dynamic_line.set_line_color(new_color)
        dynamic_line.set_width(new_width)
        pause_for_next(f"Dynamic trend line updated - Color: {new_color}, Width: {new_width}", interactive_mode, delay)
    
    logging.info(f"Dynamic trend line final ID: {dynamic_line.id}")
    
    pause_for_next("Dynamic trend line updated.", interactive_mode, delay)

    # Clean up all trend lines
    logging.info("\n=== Cleaning up all trend lines ===")
    all_lines = [
        trend_line1, trend_line2, trend_line3, trend_line4, volume_trend_line,
        channel_top, channel_bottom, resistance_level, support_level,
        custom_label_line, transparent_line, semi_transparent_line, dynamic_line
    ]
    
    for line in all_lines:
        if hasattr(line, 'delete'):
            line.delete()
    
    logging.info("All trend lines removed")
    
    logging.info("\nTrend lines test completed successfully")


def main():
    """Main function"""
    args = parse_test_arguments("Trend Lines Test - Testing various trend line options and configurations")
    
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
        # Pass chart directly to test_trend_lines
        
        # Run test
        test_trend_lines(candlestick_series, volume_series, candlestick_data, volume_data,
                         args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()