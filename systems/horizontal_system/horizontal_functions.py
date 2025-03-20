from decimal import Decimal
import logging

from . import available_timebases
from signal_generator import N_TDIV

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_chart_xlimit(self: "Oscilloscope", timebase: Decimal, delay: Decimal = Decimal('NaN')) -> tuple[float, float]:  # type: ignore # noqa: F821
    """self.delay is specified at self.timebase and belongs to it.
    If timebase changes the delay has to remain unchanged"""
    delay: Decimal = delay
    if timebase != self.timebase:  # new timebase, old delay
        # Make sure delay stays in bounds
        delay = clamp_delay(Decimal(self.delay), timebase)
        # Make sure the clamped delay is in bounds at every moment
        self.delay = delay
    
    else:  # old timebase, new delay (from argument passed to current call)
        if delay is Decimal('NaN'):
            raise Exception("Specify `delay`.")
        delay = clamp_delay(delay, timebase)
    
    return (float(-timebase*N_TDIV/2 - delay), float(timebase*N_TDIV/2 - delay))  # type: ignore

def relim_and_update_chart(self, timebase=None, delay=None):
    if timebase is None:
        timebase = self.timebase
    if delay is None:
        delay = self.delay
    
    delay = clamp_delay(delay, timebase)
    
    if hasattr(self, "canvas"):
        new_xlim = calculate_chart_xlimit(self, timebase=timebase, delay=delay)
        self.canvas.update_chart(xlim=new_xlim)

def get_current_delay(self: "Oscilloscope", timebase: Decimal) -> Decimal:  # type: ignore # noqa: F821
    timerange = timebase * Decimal(N_TDIV)
    
    delay_position = self.triggerDelayKnob.value()
    delay_knob_range = self.triggerDelayKnob.maximum() - self.triggerDelayKnob.minimum()
    
    # Normalize the knob value (make it independent of the precision)
    normalized_position = Decimal(delay_position) / Decimal(delay_knob_range)
    delay = normalized_position * timerange
    
    delay = clamp_delay(delay, timebase)
    
    return delay

def clamp_delay(delay: Decimal, timebase: Decimal) -> Decimal:
    timerange = timebase * Decimal(N_TDIV)
    half_range = timerange / Decimal(2)
    if delay > half_range:
        return half_range
    elif delay < -half_range:
        return -half_range
    return delay

def set_triggerDelayKnob(self, delay: Decimal, timebase: Decimal):
    timerange = timebase * Decimal(N_TDIV)
    normalized_position = delay / timerange
    delay_knob_range = self.triggerDelayKnob.maximum() - self.triggerDelayKnob.minimum()
    delay_position = normalized_position * Decimal(delay_knob_range)
    self.triggerDelayKnob.setValue(int(delay_position))
    self.delay_selected.emit(delay)

def get_current_timebase(self: "Oscilloscope") -> Decimal:  # type: ignore # noqa: F821
    return available_timebases[self.horizontalScaleKnob.value()]

def set_horizontalScaleKnob(self, timebase: Decimal):
        if timebase in available_timebases:
            index = available_timebases.index(timebase)
            self.horizontalScaleKnob.setValue(index)
        else:
            raise ValueError("Invalid timebase")

def adjust_horizontal_scale(self: "Oscilloscope") -> Decimal:  # type: ignore # noqa: F821
    """Turn the **HORIZONTAL Scale Knob** on the front panel to adjust the horizontal time base. 
    Turn clockwise to reduce the horizontal time base and turn counterclockwise to increase.
    
    The time base information at the upper left corner of the screen will change accordingly 
    during the adjustment. The range of the horizontal scale is from 1ns/div to 100s/div. 
    
    The **Horizontal Scale Knob** works (in the Normal time mode) while acquisitions are 
    running or when they are stopped. When running, adjusting the horizontal scale knob 
    changes the sample rate. When stopped, adjusting the horizontal scale knob lets you 
    zoom into acquired data."""
    timebase = get_current_timebase(self)
    
    relim_and_update_chart(self, timebase=timebase)
    set_triggerDelayKnob(self, self.delay, timebase)
    
    self.timebase = timebase  # update self.timebase AFTER calculate_chart_xlimit() for its next call
    self.timebase_selected.emit(self.timebase)
    return self.timebase

def adjust_trigger_delay(self: "Oscilloscope"):  # type: ignore # noqa: F821
    """Turn the Position Knob on the front panel to adjust the trigger delay of the waveform. 
    During the modification, waveforms of all the channels would move left or right and the 
    trigger delay message at the upper-right corner of the screen would change accordingly. 
    Press down this knob to quickly reset the trigger delay. 
    
    Changing the delay time moves the trigger point (solid inverted triangle) horizontally and 
    indicates how far it is from the time reference point. These reference points are indicated 
    along the top of the display grid. 
    
    All events displayed left of the trigger point happened before the trigger occurred. These 
    events are called pre- trigger information, and they show events that led up to the trigger 
    point. 
    
    Everything to the right of the trigger point is called post- trigger information. The amount of 
    delay range (pre- trigger and post- trigger information) available depends on the time/div 
    selected and memory depth. 
    
    The position knob works (in the Normal time mode) while acquisitions are running or when 
    they are stopped. When running, adjusting the horizontal scale knob changes the sample 
    rate. When stopped, adjusting the horizontal scale knob lets you zoom into acquired data."""
    delay = get_current_delay(self, timebase = self.timebase)
    
    relim_and_update_chart(self, delay=delay)
    
    self.delay = delay  # update self.delay AFTER calculate_chart_xlimit() for its next call
    self.delay_selected.emit(delay)
    return delay

def set_roll_mode(self, state: bool):
    """Press the **Roll** button to enter the roll mode. 
    
    In Roll mode the waveform moves slowly across the screen from right to left. It only 
    operates on time base settings of 50 ms/div and slower. If the current time base setting is 
    faster than the 50 ms/div limit, it will be set to 50 ms/div when Roll mode is entered. 
    
    In Roll mode there is no trigger. The fixed reference point on the screen is the right edge 
    of the screen and refers to the current moment in time. Events that have occurred are 
    scrolled to the left of the reference point. Since there is no trigger, no pre- trigger 
    information is available. 
    
    If you would like to stop the display in Roll mode, press the **Run/Stop** button. To clear the 
    display and restart an acquisition in Roll mode, press the **Run/Stop** button again. 
    
    Use Roll mode on low- frequency waveforms to yield a display much like a strip chart 
    recorder. It allows the waveform to roll across the display.
    """
    logging.debug('Entered roll mode')
    if isinstance(state, bool):
        self.roll_mode = state
    else:
        logging.error('Invalid roll mode state. Expected boolean')

def use_zoom_function(self):
    """Zoom is a horizontally expanded version of the normal display. You can use Zoom to 
    locate and horizontally expand part of the normal window for a more detailed (higher- 
    resolution) analysis of signals. 
    
    Press the **HORIZONTAL Scale Knob** on the front panel to turn on the zoom function, and 
    press the button again to turn off the function. When Zoom function is on, the display 
    divides in half. The top half of the display shows the normal time base window and the 
    bottom half displays a faster Zoom time base window.
    
    The area of the normal display that is expanded is outlined with a box and the rest of the 
    normal display is ghosted. The box shows the portion of the normal sweep that is 
    expanded in the lower half.
    
    To change the time base for the Zoom window, turn the **Horizontal Scale Knob**. The 
    **Horizontal Scale Knob** controls the size of the box. The **Horizontal Position Knob** sets 
    the left- to- right position of the zoom window. The delay value, which is the time displayed 
    relative to the trigger point is momentarily displayed in the upper- right corner of the 
    display when the **Horizontal Position Knob** is turned. Negative delay values indicate 
    you're looking at a portion of the waveform before the trigger event, and positive values 
    indicate you're looking at the waveform after the trigger event. 
    
    To change the time base of the normal window, turn off Zoom; then, turn the **Horizontal 
    Scale Knob**. 
    """
    pass