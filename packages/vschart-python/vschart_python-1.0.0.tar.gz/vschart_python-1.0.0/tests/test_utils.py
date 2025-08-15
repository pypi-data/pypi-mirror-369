#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test utilities module
Provides shared functions and utilities for testing
"""

import argparse
import time
import random
import sys
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any

from pandas.core.missing import F
from rich.console import Console
from rich.logging import RichHandler
import logging

from vschart import Chart, CandlestickSeries, VolumeSeries
from vschart.constants import Color

from vschart.types import to_timestamp

def configure_logger():
    """
    Configures the root logger to use RichHandler for pretty console output.
    """
    console = Console()
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_time=True, show_level=True, show_path=False)]
    )
    global logger
    logger = logging.getLogger(__name__)


console = Console()
logger = logging.getLogger(__name__)

def pause_for_next(prompt: str = "", interactive_mode: bool = True, delay: float = 1.0) -> None:
    if not interactive_mode:
        logger.info(f"{prompt}  Waiting {delay} seconds to continue...")
        time.sleep(delay)
        return
        
    logger.info(f"{prompt}  Press space to continue, q to exit...", extra={"markup": True})
    try:
        import tty
        import termios
        
        # Save current terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            while True:
                key = sys.stdin.read(1)
                if key == ' ':
                    logger.info("✓", extra={"markup": True})
                    break
                elif key.lower() == 'q':
                    logger.info("Exiting program", extra={"markup": True})
                    sys.exit(0)
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    except (ImportError, OSError):
        # Fallback for non-terminal environments or Windows
        input("Press enter to continue...")


def generate_sample_data(days: int = 10) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate sample data for testing
    
    Args:
        days: Number of days to generate data for
        
    Returns:
        Tuple of (candlestick_data, volume_data, average_volume_data)
    """
    candlestick_data: List[Dict[str, Any]] = []
    volume_data: List[Dict[str, Any]] = []
    
    start_date = datetime(2024, 1, 1)
    price = 100.0
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        timestamp = to_timestamp(current_date)
        
        # Generate random price movements
        open_price = price + random.uniform(-2, 2)
        close_price = open_price + random.uniform(-3, 3)
        high_price = max(open_price, close_price) + random.uniform(0, 2)
        low_price = min(open_price, close_price) - random.uniform(0, 2)
        volume = random.randint(100000, 1000000)
        
        candlestick_data.append({
            'time': timestamp,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2)
        })
        
        volume_data.append({
            'time': timestamp,
            'value': volume,
            'color': 'rgba(0, 150, 136, 0.8)' if close_price >= open_price else 'rgba(255, 82, 82, 0.8)'
        })
        
        price = close_price
    
    # Calculate average volume (simple moving average with window of 5)
    average_volume_data: List[Dict[str, Any]] = []
    window_size = 5
    
    for i in range(len(volume_data)):
        if i < window_size - 1:
            # Use average of available data for initial points
            avg_volume = sum(v['value'] for v in volume_data[:i+1]) / (i + 1)
        else:
            # Use rolling window average
            avg_volume = sum(v['value'] for v in volume_data[i-window_size+1:i+1]) / window_size
            
        average_volume_data.append({
            'time': volume_data[i]['time'],
            'value': avg_volume
        })
        
    return candlestick_data, volume_data, average_volume_data


def create_test_chart(host: str = "localhost", port: int = 8082) -> Chart:
    """
    Create test chart
    
    Args:
        host: WebSocket host address
        port: WebSocket port number
        
    Returns:
        Chart instance
    """
    logger.info(f"Connecting to chart server {host}:{port}")
    chart = Chart(host=host, port=port)
    if not chart.connect():
        raise ConnectionError("Cannot connect to VSCode extension")
    
    chart.create()
    chart.apply_default_chart_options()
    return chart


def setup_test_environment(chart: Chart, days: int = 30) -> Tuple[CandlestickSeries, VolumeSeries, List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Setup test environment, create candlestick and volume series
    
    Args:
        chart: Chart instance
        days: Number of days of data
        
    Returns:
        Tuple of (candlestick_series, volume_series, candlestick_data, volume_data, average_volume_data)
    """
    logger.info("Clearing chart")
    chart.clear_chart()
    
    # Generate sample data
    logger.info(f"Generating {days} days of sample data")
    candlestick_data, volume_data, average_volume_data = generate_sample_data(days)
    
    # Create candlestick series (in pane 0)
    logger.info("Creating candlestick series in pane 0")
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
    logger.info("Creating volume series in pane 1")
    volume_series = chart.add_histogram_series(
        pane=1,
        color='rgba(76, 175, 80, 0.5)',
        scale_margin_top=0.7,
        scale_margin_bottom=0
    )
    volume_series.set_data(volume_data)
    
    height = chart.get_options()['height']
    chart.set_pane_height(0, int(height * 0.7))
    
    logger.info("Adjusting chart display")
    chart.fit_content()
    
    return candlestick_series, volume_series, candlestick_data, volume_data, average_volume_data


def parse_test_arguments(description: str) -> argparse.Namespace:
    """
    Parse test command line arguments
    
    Args:
        description: Test description
        
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="WebSocket host address"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8082,
        help="WebSocket port number"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to generate data for"
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Test step interval time (seconds)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode (press space to control steps)"
    )
    
    return parser.parse_args()