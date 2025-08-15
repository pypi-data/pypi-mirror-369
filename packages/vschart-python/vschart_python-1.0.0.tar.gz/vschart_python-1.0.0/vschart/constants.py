from re import A
from token import STAR
from typing import Dict, Any

class CrosshairMode:
    NORMAL = 0
    MAGNET = 1
    HIDDEN = 2
    MAGNETOHLC = 3

# Line Style Constants
class LineStyle:
    SOLID = 0
    DOTTED = 1
    DASHED = 2
    LARGE_DASHED = 3
    SPARSE_DOTTED = 4

# Line Type Constants
class LineType:
    SIMPLE = 0
    WIDTHSTEPS = 1
    CURVED = 2

# Price Line Style Constants
class PriceLineStyle:
    SOLID = 0
    DOTTED = 1
    DASHED = 2
    LARGE_DASHED = 3
    SPARSE_DOTTED = 4
    
class MarkerPosition:
    ABOVE_BAR = 'aboveBar'
    BELOW_BAR = 'belowBar'
    IN_BAR = 'inBar'
    
class TextPosition:
    ABOVE = 'above'
    BELOW = 'below'
    
class MarkerShape:
    CIRCLE = 'circle'
    SQUARE = 'square'
    ARROW_UP = 'arrowUp'
    ARROW_DOWN = 'arrowDown'
    STAR = 'star'
    DIAMOND = 'diamond'
    TRIANGLE_UP = 'triangleUp'
    TRIANGLE_DOWN = 'triangleDown'
    RING = 'ring'
    CROSS = 'cross'
    
class Size:
    XS = 4
    S = 8
    M = 12
    L = 16
    XL = 20
    XXL = 24
    XXXL = 28
    XXXXL = 32
    

class LastPriceAnimationMode:
    DISABLED = 0
    CONTINUOUS = 1
    ONDATAUPDATE = 2

# Common Colors
class Color:
    BLACK = '#000000'
    BLUE = '#0000FF'
    BLUEVIOLET = '#8A2BE2'
    BLUE_BACKGROUND = 'rgba(0, 100, 255, 0.8)'
    BRIGHT_BLUE = '#2196F3'
    BRIGHT_GREEN = '#4CAF50'
    BRIGHT_RED = '#FF5252'
    BROWN = '#A52A2A'
    CORAL = '#FF7F50'
    CORAL_RED = '#ef5350'
    CYAN = '#00FFFF'
    CYAN_FILL = 'rgba(0, 255, 255, 0.12)'
    DARKORANGE = '#FF8C00'
    DARK_GRAY = '#191919'
    DARK_GRAY = '#404040'
    DARK_GREEN = '#137363'
    DARK_RED = '#7F0000'
    FOREST_GREEN = '#378658'
    GOLD = '#FFD700'
    GRAY = '#808080'
    GREEN = '#00FF00'
    GREEN_FILL = 'rgba(0, 255, 0, 0.08)'
    INDIGO = '#4B0082'
    LIGHT_BLUE_FILL = 'rgba(0, 100, 255, 0.15)'
    LIGHT_GRAY = '#D3D3D3'
    MAGENTA = '#FF00FF'
    MAROON = '#800000'
    NAVY = '#000080'
    OLIVE = '#808000'
    ORANGE = '#FFA500'
    ORANGE_FILL = 'rgba(255, 140, 0, 0.25)'
    PINK = '#FFC0CB'
    PURE_GREEN = '#00ff00'
    PURE_RED = '#ff0000'
    PURPLE = '#800080'
    RED = '#FF0000'
    RED_FILL = 'rgba(255, 0, 0, 0.1)'
    SILVER = '#C0C0C0'
    SLATE_GRAY = '#737375'
    SOFT_ROYAL_BLUE = 'rgba(80, 80, 255, 0.8)'
    TEAL = '#008080'
    TEAL_GREEN = '#26a69a'
    TRANS_AZURE = 'rgba(0, 0, 255, 0.2)'
    TRANS_BLUE = 'rgba(33, 150, 243, 0.1)'
    TRANS_CRIMSON = 'rgba(255, 0, 0, 0.3)'
    TRANS_EMERALD = 'rgba(0, 255, 0, 0.2)'
    TRANS_GREEN = 'rgba(0, 150, 136, 0.8)'
    TRANS_RED = 'rgba(255, 82, 82, 0.8)'
    TRANS_WHITE = 'rgba(255, 255, 255, 0.85)'
    TURQUOISE = '#40E0D0'
    VIOLET = '#EE82EE'
    VOLUME_BLUE_BAR = 'rgba(80, 80, 255, 0.8)'
    VOLUME_BLUE_FILL = 'rgba(0, 0, 255, 0.2)'
    VOLUME_GREEN_BAR = '#00ff00'
    VOLUME_GREEN_FILL = 'rgba(0, 255, 0, 0.2)'
    VOLUME_RED_BAR = '#ff0000'
    VOLUME_RED_FILL = 'rgba(255, 0, 0, 0.3)'
    WHITE = '#FFFFFF'
    WHITE_BACKGROUND_70 = 'rgba(255, 255, 255, 0.7)'
    WHITE_BACKGROUND_80 = 'rgba(255, 255, 255, 0.8)'
    WHITE_BACKGROUND_90 = 'rgba(255, 255, 255, 0.9)'
    WHITE_BACKGROUND_95 = 'rgba(255, 255, 255, 0.95)'
    YELLOW = '#FFFF00'
