"""This module contains all functions that are responsible for updating the Oscilloscope's screen view.
So all changes that happen to plotted signals, labels and other user information updates happen here.
"""

import logging
from decimal import Decimal

from packages.numbers.utils import get_multiplier_letter

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def update_timebase_label(self, timebase: Decimal):
    # logging.debug(f"The {timebase} S/div selected")
    
    base, _, letter = get_multiplier_letter(timebase)
    
    self.settings["Horizontal"]["letter"] = letter
    
    # logging.debug(f"{base} {letter}S/div")
    self.timebaseLabel.setText(f"{int(base)} {letter}s/")

def update_delay_label(self, delay):
    # active_channels = int(self.channel1["Enabled"]) + int(self.channel2["Enabled"])
    # if active_channels:
    base, _, letter = get_multiplier_letter(delay)
    
    def format_number(number):
        if number < 10:
            return f"{number:.3f}"
        elif number < 100:
            return f"{number:.2f}"
        elif number < 1000:
            return f"{number:.1f}"
        else:
            return f"{number:.0f}"
        
    self.delayLabel.setText(f"Delay: {format_number(base)} {letter}s")

def downsample(t, wfm, factor=10_000):
    t_downsampled = t[::factor]
    wfm_downsampled = wfm[::factor]
    return t_downsampled, wfm_downsampled

def update_plotted_signal(self, channel, t, wfm):
    if not self.canvas:
        logging.error("Activate front panel with activate_front_panel() from front_panel.__init__")
        return
    
    t, wfm = downsample(t, wfm)
    
    if channel == 1 and hasattr(self, "channel1"):
        if self.channel1["Enabled"]:
            self.canvas.channel1_line.set_data(t, wfm)
        else:
            self.canvas.channel1_line.set_data([], [])
    elif channel == 2 and hasattr(self, "channel2"):
        if self.channel2["Enabled"]:
            self.canvas.channel2_line.set_data(t, wfm)
        else:
            self.canvas.channel2_line.set_data([], [])
    else:
        logging.error("Invalid channel number. Accepts only 1 and 2.")
        return
    
    self.canvas.draw_idle()