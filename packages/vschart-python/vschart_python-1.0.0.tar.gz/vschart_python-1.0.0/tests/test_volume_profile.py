#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Profile Test
Testing volume profile creation, configuration, and deletion functionality
"""

import logging
from typing import List, Dict, Any

from vschart import CandlestickSeries, VolumeSeries
from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_volume_profile(candlestick_series: CandlestickSeries, volume_series: VolumeSeries,
                       candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                       delay: float, interactive_mode: bool) -> None:
    """
    Test volume profile creation, configuration, and deletion functionality
    
    Args:
        candlestick_series: Candlestick series
        candlestick_data: Candlestick chart data
        volume_data: Volume data
        delay: Operation delay between actions
        interactive_mode: Whether in interactive mode
    """
    logging.info("Starting volume profile functionality test...")
    volume_profiles = []
    
    # Prepare volume profile data
    def prepare_volume_profile_data(start_idx, end_idx):
        """Prepare volume profile data"""
        data = []
        for i in range(start_idx, min(end_idx + 1, len(candlestick_data))):
            data.append({
                'price': float(candlestick_data[i]['close']),
                'volume': float(volume_data[i]['value']) if i < len(volume_data) else 1000.0
            })
        return data

    # Volume profile 1: Standard configuration
    logging.info("Adding volume profile 1: Standard configuration...")
    start_index_1 = len(candlestick_data) * 1 // 10
    end_index_1 = len(candlestick_data) * 3 // 10
    
    profile_data_1 = prepare_volume_profile_data(start_index_1, end_index_1)
    
    vp_1 = candlestick_series.add_volume_profile(
        data=profile_data_1,
        start_time=candlestick_data[start_index_1]['time'],
        end_time=candlestick_data[end_index_1]['time'],
        fill_color='rgba(33, 150, 243, 0.6)',
        bar_color='rgba(33, 150, 243, 1)',
        opacity=0.6,
        background_color='rgba(200, 200, 200, 0.1)',
        border_color='rgba(100, 100, 100, 0.3)',
        border_width=1,
        number_of_bins=50
    )
    volume_profiles.append(vp_1)
    logging.info(f"Volume profile 1 added, ID: {vp_1.id}")

    # Volume profile 2: Red configuration
    logging.info("Adding volume profile 2: Red configuration...")
    start_index_2 = len(candlestick_data) * 3 // 10
    end_index_2 = len(candlestick_data) * 5 // 10
    
    profile_data_2 = prepare_volume_profile_data(start_index_2, end_index_2)
    
    vp_2 = candlestick_series.add_volume_profile(
        data=profile_data_2,
        start_time=candlestick_data[start_index_2]['time'],
        end_time=candlestick_data[end_index_2]['time'],
        fill_color='rgba(255, 82, 82, 0.5)',
        bar_color='rgba(255, 82, 82, 1)',
        opacity=0.5,
        background_color='rgba(200, 200, 200, 0.1)',
        border_color='rgba(100, 100, 100, 0.3)',
        border_width=1,
        number_of_bins=30
    )
    volume_profiles.append(vp_2)
    logging.info(f"Volume profile 2 added, ID: {vp_2.id}")

    # Volume profile 3: Green configuration
    logging.info("Adding volume profile 3: Green configuration...")
    start_index_3 = len(candlestick_data) * 5 // 10
    end_index_3 = len(candlestick_data) * 7 // 10
    
    profile_data_3 = prepare_volume_profile_data(start_index_3, end_index_3)
    
    vp_3 = candlestick_series.add_volume_profile(
        data=profile_data_3,
        start_time=candlestick_data[start_index_3]['time'],
        end_time=candlestick_data[end_index_3]['time'],
        fill_color='rgba(76, 175, 80, 0.4)',
        bar_color='rgba(76, 175, 80, 1)',
        opacity=0.4,
        background_color='rgba(200, 200, 200, 0.1)',
        border_color='rgba(100, 100, 100, 0.3)',
        border_width=1,
        number_of_bins=40
    )
    volume_profiles.append(vp_3)
    logging.info(f"Volume profile 3 added, ID: {vp_3.id}")
    
    # Volume profile 4: Purple configuration, no text
    logging.info("Adding volume profile 4: Purple configuration, no text...")
    start_index_4 = len(candlestick_data) * 7 // 10
    end_index_4 = len(candlestick_data) * 9 // 10
    
    profile_data_4 = prepare_volume_profile_data(start_index_4, end_index_4)
    
    vp_4 = candlestick_series.add_volume_profile(
        data=profile_data_4,
        start_time=candlestick_data[start_index_4]['time'],
        end_time=candlestick_data[end_index_4]['time'],
        fill_color='rgba(156, 39, 176, 0.7)',
        bar_color='rgba(156, 39, 176, 1)',
        opacity=0.7,
        background_color='rgba(200, 200, 200, 0.1)',
        border_color='rgba(100, 100, 100, 0.3)',
        border_width=1,
        number_of_bins=25
    )
    volume_profiles.append(vp_4)
    logging.info(f"Volume profile 4 added, ID: {vp_4.id}")
    
    # Volume profile 5: Orange configuration, high density
    logging.info("Adding volume profile 5: Orange configuration, high density...")
    start_index_5 = len(candlestick_data) * 2 // 10
    end_index_5 = len(candlestick_data) * 4 // 10
    
    profile_data_5 = prepare_volume_profile_data(start_index_5, end_index_5)
    
    vp_5 = candlestick_series.add_volume_profile(
        data=profile_data_5,
        start_time=candlestick_data[start_index_5]['time'],
        end_time=candlestick_data[end_index_5]['time'],
        fill_color='rgba(255, 140, 0, 0.3)',
        bar_color='rgba(255, 140, 0, 1)',
        opacity=0.3,
        background_color='rgba(200, 200, 200, 0.1)',
        border_color='rgba(100, 100, 100, 0.3)',
        border_width=1,
        number_of_bins=60
    )
    volume_profiles.append(vp_5)
    logging.info(f"Volume profile 5 added, ID: {vp_5.id}")
    
    # Volume profile 6: Cyan configuration, low density
    logging.info("Adding volume profile 6: Cyan configuration, low density...")
    start_index_6 = len(candlestick_data) * 6 // 10
    end_index_6 = len(candlestick_data) * 8 // 10
    
    profile_data_6 = prepare_volume_profile_data(start_index_6, end_index_6)
    
    vp_6 = candlestick_series.add_volume_profile(
        data=profile_data_6,
        start_time=candlestick_data[start_index_6]['time'],
        end_time=candlestick_data[end_index_6]['time'],
        fill_color='rgba(0, 188, 212, 0.6)',
        bar_color='rgba(0, 188, 212, 1)',
        opacity=0.6,
        background_color='rgba(200, 200, 200, 0.1)',
        border_color='rgba(100, 100, 100, 0.3)',
        border_width=1,
        number_of_bins=15
    )
    volume_profiles.append(vp_6)
    logging.info(f"Volume profile 6 added, ID: {vp_6.id}")
    
    # Display all volume profiles
    pause_for_next("All volume profiles added.", interactive_mode, delay * 2)
    
    # Modify configuration individually
    for i, vp in enumerate(volume_profiles, 1):
        logging.info(f"Modifying color of volume profile {i}...")
        
        # Select different colors based on index
        colors = [
            'rgba(255, 0, 0, 0.5)',
            'rgba(0, 255, 0, 0.5)',
            'rgba(0, 0, 255, 0.5)',
            'rgba(255, 255, 0, 0.5)',
            'rgba(255, 0, 255, 0.5)',
            'rgba(0, 255, 255, 0.5)'
        ]
        
        if i <= len(colors):
            vp.set_fill_color(colors[i-1])
            logging.info(f"Volume profile {i} fill color modified to {colors[i-1]}")
        
        if i < len(volume_profiles):
            pause_for_next(f"Modified volume profile {i}.", interactive_mode, delay * 0.5)
    
    # Modify border width individually
    for i, vp in enumerate(volume_profiles, 1):
        logging.info(f"Modifying border width of volume profile {i}...")
        
        # Set different border widths
        border_widths = [1, 2, 3, 4, 5, 6]
        
        if i <= len(border_widths):
            vp.set_border_width(border_widths[i-1])
            logging.info(f"Volume profile {i} border width modified to {border_widths[i-1]}")
        
        if i < len(volume_profiles):
            pause_for_next(f"Modified volume profile {i} border width.", interactive_mode, delay * 0.5)
    
    # Display final configuration
    pause_for_next("All configurations modified.", interactive_mode, delay)
    
    # Remove volume profiles individually
    for i, vp in enumerate(volume_profiles, 1):
        logging.info(f"Removing volume profile {i}...")
        vp.delete()
        logging.info(f"Volume profile {i} removed")
        
        if i < len(volume_profiles):  # Don't wait after removing the last one
            pause_for_next(f"Removed volume profile {i}.", interactive_mode, delay * 0.5)
    
    logging.info("Volume profile test completed")


def main():
    """Main function"""
    args = parse_test_arguments("Volume profile test - Testing volume profile creation, configuration, and deletion functionality")
    
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
        test_volume_profile(candlestick_series, volume_series, 
                          candlestick_data, volume_data,
                          args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()