#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tooltip Test
Testing tooltip addition, styling configuration, and functionality
"""

import time
import logging

from typing import List, Dict, Any

from vschart import Chart, CandlestickSeries, Tooltip
from vschart.constants import Color, CrosshairMode

from test_utils import (
    create_test_chart, setup_test_environment, parse_test_arguments,
    pause_for_next, configure_logger
)

configure_logger()


def test_tooltip(candlestick_series: CandlestickSeries, volume_series,
                           candlestick_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]],
                           delay: float, interactive_mode: bool) -> None:
    # Test 1: Add default tooltip to candlestick series
    logging.info("\n1. Adding default tooltip to candlestick series")
    tooltip1 = candlestick_series.add_tooltip()
    pause_for_next("Hover over the chart to see the default tooltip...", interactive_mode)
    
    # Test 2: Configure tooltip with title
    logging.info("\n2. Setting tooltip title")
    tooltip1.set_title("OHLC Values")
    pause_for_next("Hover over the chart to see the tooltip with title...", interactive_mode)
    
    # Test 3: Set tooltip Y position
    logging.info("\n3. Setting tooltip Y position")
    tooltip1.set_y_position(50)
    pause_for_next("Hover over the chart to see the tooltip at the specified Y position...", interactive_mode)
    
    # Test 5: Change tooltip background color
    logging.info("\n5. Changing tooltip background color")
    tooltip1.set_background_color("rgba(50, 50, 50, 0.9)")
    pause_for_next("Hover over the chart to see the tooltip with new background color...", interactive_mode)
    
    # Test 6: Change tooltip text color
    logging.info("\n6. Changing tooltip text color")
    tooltip1.set_text_color(Color.BRIGHT_GREEN)
    pause_for_next("Hover over the chart to see the tooltip with new text color...", interactive_mode)
    
    # Test 7: Change tooltip font size
    logging.info("\n7. Changing tooltip font size")
    tooltip1.set_font_size(14)
    pause_for_next("Hover over the chart to see the tooltip with larger font size...", interactive_mode)
    
    # Test 8: Change tooltip font family
    logging.info("\n8. Changing tooltip font family")
    tooltip1.set_font_family("monospace")
    pause_for_next("Hover over the chart to see the tooltip with monospace font...", interactive_mode)
    
    # Test 9: Change tooltip padding
    logging.info("\n9. Changing tooltip padding")
    tooltip1.set_padding(12)
    pause_for_next("Hover over the chart to see the tooltip with increased padding...", interactive_mode)
    
    # Test 10: Add tooltip to volume series with custom options
    logging.info("\n10. Adding tooltip to volume series with custom options")
    tooltip2 = volume_series.add_tooltip({
        "title": "Volume",
        "backgroundColor": "rgba(0, 100, 255, 0.8)",
        "textColor": "white",
        "fontSize": 13,
        "fontFamily": "sans-serif",
        "padding": 10
    })
    pause_for_next("Hover over the volume series to see the tooltip...", interactive_mode)
    
    # Test 11: Remove tooltip from candlestick series
    logging.info("\n11. Removing tooltip from candlestick series")
    result = candlestick_series.remove_primitive(tooltip1.id)
    logging.info(f"Tooltip removal result: {result}")
    pause_for_next("Verify tooltip is removed from candlestick series...", interactive_mode)
    
    # Test 12: Change volume tooltip Y position
    logging.info("\n12. Changing volume tooltip Y position.")
    tooltip2.set_y_position(0)
    pause_for_next("Hover over the volume series to see the tooltip at the new position...", interactive_mode)
    
    # Test 13: Remove tooltip from volume series
    logging.info("\nl3. Removing tooltip from volume series")
    result = volume_series.remove_primitive(tooltip2.id)
    logging.info(f"Tooltip removal result: {result}")
    pause_for_next("Verify tooltip is removed from volume series...", interactive_mode)
    
    logging.info("\nTooltip tests completed!")

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
        test_tooltip(candlestick_series, volume_series, candlestick_data, volume_data,
                               args.delay, args.interactive)
        
    finally:
        chart.disconnect()


if __name__ == "__main__":
    main()
