import logging

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_control(self):
    """Press the **Run/Stop** or **Single** button on the front panel to run or stop the sampling 
    system of the scope. 
    * When the **Run/Stop** button is green, the oscilloscope is running, that is, acquiring data 
    when trigger conditions are met. To stop acquiring data, press the **Run/Stop** button.  
    When stopped, the last acquired waveform is displayed. 
    * When the **Run/Stop** button is red, data acquisition is stopped. Red "Stop" is 
    displayed next to the trademark logo in the status line at the top of the display. To 
    start acquiring data, press **Run/Stop**. 
    * To capture and display a single acquisition (whether the oscilloscope is running or 
    stopped), press **Single**. The **Single** run control lets you view single- shot events 
    without subsequent waveform data overwriting the display. Use **Single** when you 
    want maximum memory depth for pan and zoom. 
    
    When you press **Single**, the display is cleared, the trigger mode is temporarily set to 
    Normal (to keep the oscilloscope from auto- triggering immediately), the trigger circuitry is 
    armed, the **Single** key is illuminated, and the oscilloscope waits until a user defined 
    trigger condition occurs before it displays a waveform. 
    
    When the oscilloscope triggers, the single acquisition is displayed and the oscilloscope is 
    stopped (the **Run/Stop** button is illuminated in red). 
    
    Press **Single** again to acquire another waveform"""
    pass

def select_memory_depth(self):
    """Memory depth refers to the number of waveform points that the oscilloscope can store in a 
    single trigger sample and it reflects the storage ability of the sample memory. The 
    oscilloscope provides up to 14 Mpts memory depth. 
    
    Press the **Acquire** button on the front panel; press the **Mem Depth** softkey and then turn 
    the **Universal Knob** to select the desired value and push down the knob to confirm. Press 
    the **Mem Depth** softkey continually can also select the desired value. 
    
    The actual memory depth is displayed in the information area at the upper- right corner of 
    the screen. Memory depth that available: 14K, 140K, 1.4M, 14M. 
    
    Since the oscilloscope has two acquisition memories, when only one channel is on, the 
    maximal memory depth is up to 14 Mpts. 
    
    The relation of memory depth, sample rate and waveform length fulfills the equation 
    below:  
    
    Memory depth = sample rate (Sa/s) × waveform length (s/div × div)"""
    
def select_sampling_mode(self):
    """The oscilloscope only supports real-time sample. In this mode, the oscilloscope samples 
    and displays waveform within a trigger event. The maximum real-time sample rate is 
    1GSa/s. 
    
    Press the **RUN/STOP** button to stop the sample, the oscilloscope will hold the last display. 
    At this point, you can still use the vertical control and horizontal control to pan and zoom 
    the waveform. """
    pass

def select_waveform_interpolation_method(self):
    """Under real-time sampling, the oscilloscope acquires the discrete sample values of the 
    waveform being displayed. In general, a waveform of dots display type is very difficult to 
    observe. In order to increase the visibility of the signal, the digital oscilloscope usually 
    uses the interpolation method to display a waveform. 
    
    Interpolation method is a processing method to “connect all the sampling points”, and 
    using some points to calculate the whole appearance of the waveform. For real-time 
    sampling interpolation method is used, even if the oscilloscope in a single captures only a 
    small number of sampling points. The oscilloscope can use interpolation method for filling 
    out the gaps between points, to reconstruct an accurate waveform. 
    
    Press the **Acquire** button on the front panel to enter the ACQUIRE Function menu; then 
    press the **Interpolation*** softkey to select **Sinx/x** or **X**. 
    * **X**: In the adjacent sample points are directly connected on a straight line. This 
    method is only confined to rebuild on the edge of signals, such as square wave. 
    * **Sinx/x**: Connecting the sampling points with curves has stronger versatility. Sinx 
    interpolation method uses mathematical processing to calculation results in the actual 
    sample interval. This method bending signal waveform, and make it produce more 
    realistic regular shape than pure square wave and pulse. When the sampling rate is 3 
    to 5 times the bandwidth of the system. Recommended Sinx/s interpolation method."""
    pass

def select_acquisition_mode(self):
    """The acquisition mode is used to control how to generate waveform points from sample 
    points. The oscilloscope provides the following acquisition mode: Normal, Peak Detect, 
    Average and High Resolution. 
    1. Press the **Acquire** button on the front panel to enter the ACQUIRE function menu; 
    2. Press the **Acquisition** softkey; then turn the **Universal Knob** to select the desired 
    acquisition mode and push down the knob to confirm. The default setup is **Normal**. 
    
    **Normal**
    
    In this mode, the oscilloscope samples the signal at equal time interval to rebuild the 
    waveform. For most of the waveforms, the best display effect can be obtained using this 
    mode. It is the default acquisition mode.
    
    **Peak Detect**
    
    In this mode, the oscilloscope acquires the maximum and minimum values of the signal 
    within the sample interval to get the envelope of the signal or the narrow pulse of the 
    signal that might be lost. In this mode, signal confusion can be prevented but the noise 
    displayed would be larger.
    
    In this mode, the oscilloscope can display all the pulses with pulse widths at least as wide 
    as the sample period.
    
    **Average**
    
    In this mode, the oscilloscope averages the waveforms from multiple samples to reduce 
    the random noise of the input signal and improve the vertical resolution. The greater the 
    number of averages is, the lower the noise will be and the higher the vertical resolution will 
    be but the slower the response of the displayed waveform to the waveform changes will 
    be.  
    
    The available range of averages is from 4 to 1024 and the default is 16. When **Average**
    mode is selected, press **Averages** and turn the universal knob or press the softkey 
    continually to set the desired average time. 
    
    **High Resolution**
    
    This mode uses a kind of ultra-sample technique to average the neighboring points of the 
    sample waveform to reduce the random noise on the input signal and generate much 
    smoother waveforms on the screen. This is generally used when the sample rate of the 
    digital converter is higher than the storage rate of the acquisition memory.  
    High Resolution mode can be used on both single- shot and repetitive signals and it does 
    not slow waveform update. This mode limits the oscilloscope's real-time bandwidth 
    because it effectively acts like a low- pass filter.
    
    **Note: “Average” and “High Res” modes use different averaging methods. The former uses 
    “Waveform Average” and the latter uses “Dot Average”.**

    """
    pass

def change_horizontal_format(self):
    """Press the **Acquire** button on the front panel; then press the **XY** soft key to set the XY(On) 
    or YT(Off) mode. The default setup is **YT**.
    
    **YT**
    
    It is the normal viewing mode for the oscilloscope. In the Normal time mode, signal events 
    occurring before the trigger are plotted to the left of the trigger point and signal events 
    after the trigger plotted to the right of the trigger point.
    
    **XY**
    
    XY mode changes the display from a volt- versus- time display to a volt- versus- volt 
    display. Channel 1 amplitude is plotted on the X- axis and Channel 2 amplitude is plotted 
    on the Y- axis, the two channels will be turned on or off together. 
    
    You can use XY mode to compare frequency and phase relationships between two 
    signals. XY mode can also be used with transducers to display strain versus displacement, 
    flow versus pressure, volts versus current, or voltage versus frequency. 
    
    The phase deviation between two signals with the same frequency can be easily 
    measured via Lissajous method.
    
    According to **sinθ=A/B** or **C/D**, wherein θ is the phase deviation angle between the two 
    channels and the definitions of A, B, C and D are:
    * **A**, the positive amplitude of the signal crossing Y-axis at X=0 (I or II quadrant)
    * **B**, the positive amplitude of the signal (I or II quadrant)
    * **C**, the sum of Y-axis crossing point absolute values at X=0 (I and III quadrants or II and IV quadrants)
    * **D**, the sum of the absolute values of the signal amplitude (I and III quadrants or II and IV quadrants)
       
    the phase deviation angle is obtained, that is: **θ=±arcsin (A/B)** or **±arcsin (C/D)**.
    
    If the principal axis of the ellipse is within quadrant I and III, the phase deviation angle 
    obtained should be within quadrant I and IV, namely within (0 to π/2) or (3π/2 to 2π). If the 
    principal axis of the ellipse is within quadrant II and IV, the phase deviation angle obtained 
    should be within quadrant II and III, namely within (π/2 to π) or (π to 3π/2).  
    
    X-Y function can be used to measure the phase deviation occurred when the signal under 
    test passes through a circuit network. Connect the oscilloscope to the circuit to monitor the 
    input and output signals of the circuit. """
    pass

def use_sequence_mode(self):
    """Sequence is also a kind of acquisition mode, which does not display waveform during 
    sampling process. It improves the waveform capture rate, and the maximal capture rate is 
    more than 400,000 wfs/s. So it can capture the small probability event effectively.  
    
    The oscilloscope runs and fills a memory segment for each trigger event. The oscilloscope 
    is busy acquiring multiple segments. The oscilloscope continues to trigger until memory is 
    filled, and then display the waveforms on the screen. 
    
    To use the sequence mode, the HORIZONTAL Format must be set to **YT**.
    
    Do the following steps to use the sequence mode. 
    1. Press the **Acquire** button on the front panel to enter the ACQUIRE function menu; 
    2. Press the **Sequence** softkey to enter the SEQUENCE function menu.
    3. Press the **Segments Set** softkey; and then turn the Universal Knob to select the 
    desired value. 
    
    Do the following steps to replay the sequence waveform under history mode: 
    1. Press the **History** softkey to enable HISTORY function . 
    2. Press the List softkey to turn on the list display. The list records the acquisition time of 
    every frame and shows the frame number that displaying on the screen. 
    3. Press the Frame No. softkey; and then turn the Universal Knob to select the frame to 
    display. 
    4. Press the **<=** softkey to replay the waveform from the current frame to 1. 
    5. Press the **||** softkey to stop replay. 
    6. Press the **=>** softkey to replay the waveform from the current frame to the last frame.  
    """