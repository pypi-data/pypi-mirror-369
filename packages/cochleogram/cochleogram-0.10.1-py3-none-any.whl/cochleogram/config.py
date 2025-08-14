CELLS = ('IHC', 'OHC1', 'OHC2', 'OHC3', 'Extra')


CHANNEL_CONFIG = {
    'CtBP2': { 'display_color': '#FF0000'},
    'MyosinVIIa': {'display_color': '#0000FF'},
    'GluR2': {'display_color': '#00FF00'},
    'GlueR2': {'display_color': '#00FF00'},
    'PMT': {'display_color': '#FFFFFF'},
    'DAPI': {'display_color': '#FFFFFF', 'visible': False},

    # Channels are tagged as unknown if there's difficulty parsing the channel
    # information from the file.
    'Unknown 1': {'display_color': '#FF0000'},
    'Unknown 2': {'display_color': '#00FF00'},
    'Unknown 3': {'display_color': '#0000FF'},
    'Unknown 4': {'display_color': '#FFFFFF'},
}


TOOL_KEY_MAP = {
    's': 'spiral',
    'e': 'exclude',
    'c': 'cells',
    't': 'tile',
}


CELL_KEY_MAP = {
    '`': 'IHC',
    'i': 'IHC',
    '1': 'OHC1',
    '2': 'OHC2',
    '3': 'OHC3',
    '4': 'Extra',
}


# These are derived from palettable.cartocolors.qualitative.Bold_5
CELL_COLORS = {
    'IHC': (0.4980392156862745, 0.23529411764705882, 0.5529411764705883),
    'OHC1': (0.06666666666666667, 0.6470588235294118, 0.4745098039215686),
    'OHC2': (0.2235294117647059, 0.4117647058823529, 0.6745098039215687),
    'OHC3': (0.9490196078431372, 0.7176470588235294, 0.00392156862745098),
    'Extra': (0.9058823529411765, 0.24705882352941178, 0.4549019607843137),
}
