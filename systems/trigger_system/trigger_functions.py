import logging

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def trigger_source(self, source):
    """The oscilloscope's trigger source includes analog channels (**CH1**, **CH2**), **EXT**, **EXT/5** and 
    **AC Line**.  
    Press the **Setup** button on the front panel to enter the TRIGGER function menu; press the 
    **Source** softkey and then turn the **Universal Knob** to select the desired trigger source.  
    The current trigger source is displayed at the upper right corner of the screen. Select 
    channel with signal input as trigger source to obtain stable trigger. 
    
    **Analog channel input:**  
    
    Signals input from analog channels **CH1** and **CH2** can all be used as the trigger source. 
    No matter whether the input of the channel selected is enabled, the channel can work 
    normally.  
    
    **External trigger input:**
      
    External trigger source can be used to connect external trigger signal to the EXT TRIG 
    channel when all of the four channels are sampling data. The trigger signal (such as 
    external clock and signal of the circuit to be tested) will be connected to **EXT** and **EXT/5**                                                                                                     
    trigger source via the **[EXT TRIG]** connector. **EXT/5** trigger source attenuates the signal 
    by a factor of 5. It extends the trigger level. You can set the trigger condition within the 
    range of trigger level (-8 div to +8 div).  
    
    **AC line:**  
    
    The trigger signal is obtained from the AC power input of the oscilloscope. This kind of 
    signals can be used to display the relationship between signal (such as illuminating device) 
    and power (power supply device). For example, it is mainly used in related measurement 
    of the power industry to stably trigger the waveform output from the transformer of a 
    transformer substation.  
    
    **Note: to select stable channel waveform as the trigger source to stabilize the display.**"""
    
    if source in self.trigger_sources:
        logging.debug(f'Trigger source set to {source}')
    else:
        logging.error('Invalid trigger source')
        return
    
    self.trigger_source = source

def trigger_mode(self, mode):
    """
    The oscilloscope's trigger mode includes auto, normal and single. Trigger mode affects
    the way in which the oscilloscope searches for the trigger 

    After the oscilloscope starts running, the oscilloscope operates by first filling the
    pre-trigger buffer. It starts searching for a trigger after the pre-trigger buffer is filled and
    continues to flow data through this buffer while it searches for the trigger. While searching
    for the trigger, the oscilloscope overflows the pre-trigger buffer and the first data put into
    the buffer is first pushed out (First Input First Out, FIFO).

    When a trigger is found, the pre-trigger buffer contains the events that occurred just
    before the trigger. Then, the oscilloscope fills the post-trigger buffer and displays the
    acquisition memory.

    Press the **Auto**, **Normal** and the **Single** buttons on the front panel to select the desired
    trigger mode, and the corresponding status light will be lighted.

    * In the **Auto** trigger mode (the default setting), if the specified trigger conditions are
      not found, triggers are forced and acquisitions are made so that signal activity is
      displayed on the oscilloscope.
      
      The Auto trigger mode is appropriate when:
      
      * Checking DC signals or signals with unknown levels or activity.
      * When trigger conditions occur often enough that forced triggers are unnecessary.

    * In the **Normal** trigger mode, triggers and acquisitions only occur when the specified
      trigger conditions are found. Otherwise, the oscilloscope holds the original waveform
      and waits for the next trigger.

      The **Normal** trigger mode is appropriate when:

      * You only want to acquire specific events specified by the trigger settings.
      * Triggering on an infrequent signal from a serial bus (for example, I2C, SPI, CAN,
        LIN, etc.) or another signal that arrives in bursts. The **Normal** trigger mode lets
        you stabilize the display by preventing the oscilloscope from auto-triggering.

    * In the **Single** trigger mode, the oscilloscope waits for a trigger and displays the
      waveform when the trigger condition is met and then stops.

      The **Single** trigger mode is appropriate when:

      * To capture a single event or aperiodic signal.
      * To capture burst or other unusual signals.
    """    
    if mode in self.trigger_modes:
        logging.debug(f'Trigger mode set to {mode}')
    else:
        logging.error('Invalid trigger mode')
        return
    
    self.trigger_mode = mode
    
def trigger_level(self, level):
    """Trigger level and slope define the trigger point, such that trigger point is the point at
    which the signal crosses the trigger level in either rising or falling direction (positive or
    negative slope).
    
    You can adjust the trigger level for a selected analog channel by turning the **Trigger Level 
    Knob**. 
    
    You can push the **Trigger Level Knob** to set the level to the waveform's 50% value 
    immediately. If AC coupling is used, pushing the **Trigger Level knob** sets the trigger level 
    to about 0 V. 
    
    The position of the trigger level for the analog channel is indicated by the trigger level icon 
    **<|** (If the analog channel is on) at the left side of the display. The value of the analog 
    channel trigger level is displayed in the upper- right corner of the display."""
    
    self.trigger_level = level

def trigger_coupling(self, mode):
    """Press the **Setup** button on the front panel to enter the TRIGGER function menu, and then 
    press the **Coupling** softkey and turn the **Universal Knob** or press the **Coupling** softkey 
    continually to select the desired coupling mode. 
    The oscilloscope provides 4 kinds of trigger coupling modes: 
    * **DC**: allow DC and AC components into the trigger path.  
    * **AC**: block all the DC components and attenuate signals lower than 5.8 Hz. Use AC 
    coupling to get a stable edge trigger when your waveform has a large DC offset. 
    * **LF Reject**: block the DC components and reject the low frequency components lower 
    than 2.08MHz. Low frequency reject removes any unwanted low frequency 
    components from a trigger waveform, such as power line frequencies, etc., that can 
    interfere with proper triggering. Use **LF Reject** coupling to get a stable edge trigger 
    when your waveform has low frequency noise. 
    * **HF Reject**: reject the high frequency components higher 1.27MHz)  
    
    **Note: trigger coupling has nothing to do with the channel coupling.** """
    if mode in self.trigger_couplings:
        logging.debug(f'Trigger coupling mode set to {mode}')
    else:
        logging.error('Invalid trigger coupling mode')
        return
    
    self.trigger_coupling = mode

def trigger_holdoff(self, holdoff_time):
    """Trigger holdoff can be used to stably trigger the complex waveforms (such as pulse 
    series). Holdoff time is the amount of time that the oscilloscope waits before re-arming the 
    trigger circuitry. The oscilloscope will not trigger until the holdoff time expires. 
    
    Use the holdoff to trigger on repetitive waveforms that have multiple edges (or other 
    events) between waveform repetitions. You can also use holdoff to trigger on the first 
    edge of a burst when you know the minimum time between bursts. 
    
    For example, to get a stable trigger on the repetitive pulse burst shown below, set the 
    holdoff time to be >200 ns but <600 ns. 
    
    The correct holdoff setting is typically slightly less than one repetition of the waveform. Set 
    the holdoff to this time to generate a unique trigger point for a repetitive waveform. Only 
    edge trigger and serial trigger have holdoff option. The holdoff time of the oscilloscope is 
    adjustable from 100ns to 1.5s. 
    
    1. Press the **Stop** button, and then use the **Horizontal Position Knob** and the 
    **Horizontal Scale Knob** to find where the waveform repeats. Measure this time using 
    cursors; then, set the holdoff. 
    2. Press the **Setup** button on the front panel to enter the TRIGGER function menu. The 
    default trigger type is edge. 
    3. Press the **Holdoff Close** softkey; and then turn the **Universal Knob** to set the desired 
    holdoff time.
    
    **Note: adjust the time scale and horizontal position will not affect the holdoff time.**"""
    pass

def noise_rejection(self):
    """Noise Reject adds additional hysteresis to the trigger circuitry. By increasing the trigger 
    hysteresis band, you reduce the possibility of triggering on noise. However, this also 
    decreases the trigger sensitivity so that a slightly larger signal is required to trigger the 
    oscilloscope. 
    
    Press the **Setup** button on the front panel, and then press the **Noise Reject** softkey 
    continually to set the option to **On** or **Off** to turn on or off the noise rejection function. 
    
    If the signal you are probing is noisy, you can set up the oscilloscope to reduce the noise 
    in the trigger path and on the displayed waveform. First, stabilize the displayed waveform 
    by removing the noise from the trigger path. Second, reduce the noise on the displayed 
    waveform. 
    1. Connect a signal to the oscilloscope and obtain a stable display. 
    2. Remove the noise from the trigger path by setting trigger coupling to **LF Reject**, **HF 
    Reject** or turning on **Noise Reject**. 
    3. Set the **Acquisition** option to Average to reduce noise on the displayed waveform."""
    pass

## HERE GO ALL THE TRIGGER TYPES ##