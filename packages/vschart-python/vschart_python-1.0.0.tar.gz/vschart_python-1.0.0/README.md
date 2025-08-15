# VSChart Python Client

A Python client for the VSChart extension, providing a Pythonic interface to create interactive financial charts in VSCode. This client communicates with the VSChart extension via WebSocket to render and manipulate financial charts directly in your VSCode environment.

[![PyPI version](https://img.shields.io/pypi/v/vschart-python.svg)](https://pypi.org/project/vschart-python/)
[![Python versions](https://img.shields.io/pypi/pyversions/vschart-python.svg)](https://pypi.org/project/vschart-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

### From PyPI

```bash
pip install vschart-python
```

### From Source

```bash
git clone https://github.com/yourusername/vschart.git
cd vschart/vschart-python
pip install -e .
```

## Features

- **Interactive Financial Charts**: Create and manipulate charts directly in VSCode
- **Multiple Chart Types**: Support for candlestick, line, and histogram series
- **Technical Analysis Tools**: Add trend lines, Fibonacci retracements, and more
- **Multi-pane Support**: Create charts with multiple panes for different indicators
- **Rich Logging**: Colored output using the Rich library
- **Type Hints**: Comprehensive type annotations for better IDE support
- **Constants Library**: Predefined constants for styles, types, and colors

## Prerequisites

- VSCode with the VSChart extension installed
- Python 3.7 or higher
- Required Python packages (automatically installed): websocket-client, numpy, pandas, rich

## Usage

### Basic Example

```python
from vschart import Chart, CandlestickSeries, VolumeSeries
import pandas as pd
import numpy as np

# Sample data generation (replace with your actual data)
def generate_sample_data(n=100):
    dates = pd.date_range(start="2023-01-01", periods=n)
    timestamps = [int(d.timestamp()) for d in dates]
    
    # Generate OHLC data
    close = 100 + np.cumsum(np.random.normal(0, 1, n))
    high = close + np.random.uniform(0, 3, n)
    low = close - np.random.uniform(0, 3, n)
    open_price = close.copy()
    np.random.shuffle(open_price)
    
    # Generate volume data
    volume = np.random.uniform(1000, 5000, n)
    
    # Create candlestick data
    candlestick_data = [
        {"time": t, "open": o, "high": h, "low": l, "close": c}
        for t, o, h, l, c in zip(timestamps, open_price, high, low, close)
    ]
    
    # Create volume data
    volume_data = [
        {"time": t, "value": v} for t, v in zip(timestamps, volume)
    ]
    
    return candlestick_data, volume_data

# Generate sample data
candlestick_data, volume_data = generate_sample_data()

# Create chart instance
chart = Chart(host="localhost", port=8080)

# Connect to the server
if chart.connect():
    # Add candlestick series
    candlestick_series = chart.add_candlestick_series()
    
    # Add volume series in a separate pane
    volume_series = chart.add_histogram_series(pane_index=1)
    
    # Set data
    candlestick_series.set_data(candlestick_data)
    volume_series.set_data(volume_data)
    
```

### Using Constants

The library provides constants for line styles, line types, price line styles, and colors to make your code more readable and maintainable:

```python
from vschart import Chart, LineSeries
from vschart import LineStyle, LineType, PriceLineStyle, Color

# Create chart instance
chart = Chart("ws://localhost:8080")

# Connect to the server
if chart.connect():
    # Add line series with constants
    line_series = chart.add_line_series(
        color=Color.BLUE,
        lineWidth=2,
        lineStyle=LineStyle.DASHED,
        lineType=LineType.SIMPLE,
        priceLineStyle=PriceLineStyle.DOTTED
    )
    
    # Set data
    line_series.set_data(line_data)
```

## Available Constants

### Line Styles

```python
LineStyle.SOLID         # 0: Solid line
LineStyle.DOTTED        # 1: Dotted line
LineStyle.DASHED        # 2: Dashed line
LineStyle.LARGE_DASHED  # 3: Large dashed line
LineStyle.SPARSE_DOTTED # 4: Sparse dotted line
```

### Line Types

```python
LineType.SIMPLE  # 0: Simple line
LineType.STEP    # 1: Step line
```

### Price Line Styles

```python
PriceLineStyle.SOLID         # 0: Solid line
PriceLineStyle.DOTTED        # 1: Dotted line
PriceLineStyle.DASHED        # 2: Dashed line
PriceLineStyle.LARGE_DASHED  # 3: Large dashed line
PriceLineStyle.SPARSE_DOTTED # 4: Sparse dotted line
```

### Colors

```python
# Basic colors
Color.BLACK    # '#000000'
Color.WHITE    # '#FFFFFF'
Color.RED      # '#FF0000'
Color.GREEN    # '#00FF00'
Color.BLUE     # '#0000FF'
Color.YELLOW   # '#FFFF00'
Color.CYAN     # '#00FFFF'
Color.MAGENTA  # '#FF00FF'

# Chart specific colors
Color.UP_COLOR     # '#26a69a' (Green for up candles)
Color.DOWN_COLOR   # '#ef5350' (Red for down candles)
Color.WICK_COLOR   # '#737375' (Default wick color)
Color.LINE_COLOR   # '#2196F3' (Default line color)
Color.VOLUME_COLOR # '#26a69a' (Default volume color)
Color.BORDER_COLOR # '#378658' (Default border color)
Color.FILL_COLOR   # 'rgba(33, 150, 243, 0.1)' (Default fill color with transparency)
```

## Examples

Check the `examples` directory for more examples:

- `basic_example.py`: Basic usage of the library
- `constants_example.py`: Example using the constants
- `rich_logging_demo.py`: Demo of the rich logging features

## Documentation

For more information, see the documentation in the `docs` directory.

## Requirements

- Python 3.7 or higher
- websocket-client>=1.6.0
- numpy>=1.21.0
- pandas>=1.3.0
- rich>=10.0.0

## License

MIT