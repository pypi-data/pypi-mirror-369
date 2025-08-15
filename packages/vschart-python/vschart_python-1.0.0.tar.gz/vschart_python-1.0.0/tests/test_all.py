#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All tests aggregator
Sequentially run all independent tests and clear chart elements before each test
"""

import time
import importlib.util
import os
import sys
from typing import List, Dict, Any

from vschart import CandlestickSeries, VolumeSeries
import logging
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


# Test module list
TEST_MODULES = [
    'test_line_series',
    'test_trend_lines', 
    'test_fibonacci',
    'test_rectangles',
    'test_custom_marker',
    'test_volume_markers',
    'test_vertical_lines',
    'test_background_color',
    'test_candlestick_options',
    'test_line_options',
    'test_volume_profile',
    'test_tooltip'
]


def clear_chart_elements(chart) -> None:
    """
    Clear all elements on the chart
    
    Args:
        chart: Chart instance
    """
    logging.info("Clearing all elements on the chart...")
    
    # Use clearChart method to clear the entire chart
    try:
        chart.clear_chart()
        logging.info("Chart cleared")
    except Exception as e:
        logging.error(f"Error clearing chart: {e}")
    
    logging.info("Chart elements cleared")


def import_test_module(module_name: str):
    """
    Dynamically import test module
    
    Args:
        module_name: Module name
        
    Returns:
        Imported module
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(current_dir, f"{module_name}.py")
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def run_single_test(module_name: str, chart, candlestick_series, volume_series, 
                   candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                   delay: float, interactive_mode: bool) -> bool:
    """
    Run a single test
    
    Args:
        module_name: Test module name
        chart: Chart instance
        candlestick_series: Candlestick series (outdated, needs recreation after clearing)
        volume_series: Volume series (outdated, needs recreation after clearing)
        candlestick_data: Candlestick data
        volume_data: Volume data
        delay: Operation delay between actions
        interactive_mode: Whether in interactive mode
        
    Returns:
        Whether the test was successful
    """
    try:
        logging.info(f"\n{'='*60}")
        logging.info(f"Starting test: {module_name}")
        logging.info(f"{'='*60}")
        
        # Clear chart elements
        clear_chart_elements(chart)
        
        # Recreate series as old series IDs may be invalid after clearing
        logging.info("Recreating chart series...")
        
        # Create candlestick series (in pane 0)
        candlestick_series = chart.add_candlestick_series(
            pane=0,
            up_color='rgba(0, 150, 136, 1)',
            down_color='rgba(255, 82, 82, 1)',
            border_visible=False,
            wick_up_color='rgba(0, 150, 136, 1)',
            wick_down_color='rgba(255, 82, 82, 1)'
        )
        candlestick_series.set_data(candlestick_data)
        
        # Create volume series (in pane 1)
        volume_series = chart.add_histogram_series(
            pane=1,
            color='rgba(76, 175, 80, 0.5)',
            scale_margin_top=0.7,
            scale_margin_bottom=0
        )
        volume_series.set_data(volume_data)
        
        height = chart.get_options()['height']
        chart.set_pane_height(0, int(height * 0.7))
        chart.fit_content()
        
        logging.info(f"Series recreated - Candlestick ID: {candlestick_series.id}, Volume ID: {volume_series.id}")
        
        # Dynamically import test module
        test_module = import_test_module(module_name)
        
        # Get test function
        test_function = getattr(test_module, module_name.replace('test_', 'test_'))
        
        # Run test
        test_function(candlestick_series, volume_series, 
                     candlestick_data, volume_data, 
                     delay, interactive_mode)
        
        logging.info(f"Test {module_name} completed")
        return True
        
    except Exception as e:
        logging.error(f"Error running test {module_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    # Create argument parser
    import argparse
    parser = argparse.ArgumentParser(description='Run all chart tests')
    parser.add_argument('--host', type=str, default='localhost', 
                       help='Chart server host address')
    parser.add_argument('--port', type=int, default=8082, 
                       help='Chart server port')
    parser.add_argument('--days', type=int, default=100, 
                       help='Number of trading days for generated data')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Operation delay between actions (seconds)')
    parser.add_argument('--interactive', action='store_true', 
                       help='Interactive mode (press space to continue)')
    parser.add_argument('--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level')
    parser.add_argument('--skip-tests', type=str, nargs='*', 
                       default=[], choices=TEST_MODULES,
                       help='Test modules to skip')
    parser.add_argument('--run-tests', type=str, nargs='*', 
                       choices=TEST_MODULES,
                       help='Only run specified test modules')
    
    args = parser.parse_args()
    
    # Set log level
    import logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Determine tests to run
    tests_to_run = []
    if args.run_tests:
        tests_to_run = [t for t in args.run_tests if t in TEST_MODULES]
    else:
        tests_to_run = [t for t in TEST_MODULES if t not in args.skip_tests]
    
    if not tests_to_run:
        logging.info("No tests to run")
        return
    
    print(f"Tests to run: {', '.join(tests_to_run)}")
    
    # Create chart
    chart = create_test_chart(args.host, args.port)
    
    try:
        # Setup test environment
        candlestick_series, volume_series, candlestick_data, volume_data, _ = setup_test_environment(
            chart, args.days
        )
        
        # Run tests
        success_count = 0
        total_count = len(tests_to_run)
        
        for i, test_module in enumerate(tests_to_run, 1):
            print(f"\nProgress: {i}/{total_count}")
            
            success = run_single_test(
                test_module, chart, candlestick_series, volume_series,
                candlestick_data, volume_data, args.delay, args.interactive
            )
            
            if success:
                success_count += 1
            
            # Pause between tests
            if i < total_count:
                pause_for_next(f"", args.interactive)
        
        # Summary
        print(f"\n{'='*60}")
        logging.info("Test run summary:")
        print(f"Total tests: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"{'='*60}")
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()