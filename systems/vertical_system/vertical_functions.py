from decimal import Decimal
import logging
from PyQt5 import QtWidgets

from front_panel.custom_widgets.offset_indicators import VerticalOffsetIndicator
from signal_generator import N_VDIV, DIAL_PREC_FACT

from . import available_scales
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def enable_channel(self, channel: int, state: bool):
    """The oscilloscope provides 2 analog input channels (CH1, CH2) and provides independent
    vertical control system for each channel. As the vertical system setting methods of both
    channels are the same, this chapter takes CH1 as an example to introduce the setting
    method of the vertical system.

    Connect a signal to the CH1 channel connector; and then press the CH1 button in the
    vertical control area (VERTICAL) at the front panel to enable CH1.

    The channel setting menu is displayed at the bottom of the screen and the channel label
    at the right side of the screen. The information displayed in the channel label is related to
    the current channel setting.

    After the channel is turned on, modify the parameters such as the vertical scale, the
    horizontal time base and the trigger mode according to the input signal to make the
    waveform display easy to observe and measure."""
    if channel in [1, 2]:
        channel_obj = getattr(self, f"channel{channel}")
        connector_state = getattr(self, f"channel{channel}_connector").isChecked()
        channel_obj.Enabled = state
        if state:
            getattr(self.canvas, f"channel{channel}_offset_indicator").show()
        else:
            getattr(self.canvas, f"channel{channel}_offset_indicator").hide()
    else:
        logging.error("Invalid channel number. Accepts 1 and 2 only.")
        return

    if state:
        # profile_in_main_thread(self.signalmanager.start_signal_generator, channel, connector_state)
        self.signalmanager.start_signal_generator(channel, connector_state)
    else:
        self.signalmanager.stop_signal_generator(channel)


def calculate_chart_ylimits(scale: Decimal, offset_data: Decimal) -> tuple[float, float]:  # type: ignore # noqa: F821
    return (
        float(-scale * N_VDIV / 2 + offset_data),
        float(scale * N_VDIV / 2 + offset_data),
    )


def get_current_scale(self: "Oscilloscope", channel: int) -> Decimal:  # type: ignore # noqa: F821
    if channel in [1, 2]:
        dial = self.channel1var_dial if channel == 1 else self.channel2var_dial
        scale = available_scales[dial.value()]
        self.scale_label.setText(f"Scale: {scale} V/")
        return scale
    else:
        logging.debug(
            f"[get_current_scale]: channel {channel} not supported. Returning Decimal(0)."
        )
        return Decimal(0)


def set_current_scale(self: "Oscilloscope", channel: int, scale: Decimal) -> None:  # type: ignore # noqa: F821
    if channel in [1, 2]:
        dial: QtWidgets.QDial = self.channel1var_dial if channel == 1 else self.channel2var_dial
        scale_int = available_scales.index(scale)
        dial.setValue(scale_int)
        self.scale_label.setText(f"Scale: {scale} V/")
    else:
        logging.debug(f"[set_current_scale]: channel {channel} not supported.")


def get_current_offset(self: "Oscilloscope", channel: int) -> Decimal:  # type: ignore # noqa: F821
    """Get current offset in data coordinates. Dials use integers and DIAL_PREC_FACT
    is always integer. Dividing these integers as Decimals keeps precision."""
    if channel in [1, 2]:
        pos_dial: QtWidgets.QDial = self.channel1pos_dial if channel == 1 else self.channel2pos_dial
        # Interpret dial value as offset after reducing by precision factor
        offset_data = Decimal(pos_dial.value()) / Decimal(DIAL_PREC_FACT)
        return Decimal(offset_data)
    else:
        logging.debug(
            f"[get_current_offset]: channel {channel} not supported. Returning Decimal(0)."
        )
        return Decimal(0)


def set_current_offset(self: "Oscilloscope", channel: int, offset_data: Decimal):  # type: ignore # noqa: F821
    if channel in [1, 2]:
        pos_dial: QtWidgets.QDial = self.channel1pos_dial if channel == 1 else self.channel2pos_dial
        offset_decimal = Decimal(offset_data) * Decimal(DIAL_PREC_FACT)
        if offset_decimal == int(offset_decimal):
            pos_dial.setValue(int(offset_decimal))
        else:
            print("offset_decimal is not integer. Loss of precision!")
    else:
        logging.debug(f"[set_current_offset]: channel {channel} not supported.")


def relim_and_update_chart(self, scale, offset_data: Decimal, channel: int):
    if hasattr(self, "canvas"):
        new_ylims = calculate_chart_ylimits(
            scale, offset_data
        )  # including offset based on position dial

        # First update axis limits so to properly calculate the indicator's position in axes coordinates
        self.canvas.update_chart(ylim=new_ylims, axis_number=channel)

        if channel in [1, 2]:
            indicator: VerticalOffsetIndicator = (
                self.canvas.channel1_offset_indicator
                if channel == 1
                else self.canvas.channel2_offset_indicator
            )
            state = self.channel1.Enabled if channel == 1 else self.channel2.Enabled
            # Use updated axis limits to change the offset_data to new axes coordinates
            offset = self.canvas.data_to_axes(float(offset_data), "y", axis_number=channel)

            # Now update indicator's position
            indicator.update_position(offset, visible=state)


def set_posdial_limits(scale, pos_dial: QtWidgets.QDial):
    """Set position dial limits in accord with the volt scale
    
    | Volt Scale              | Range of Vertical Position |
    |:-----------------------:|:--------------------------:|
    | 500 μV/div - 100 mV/div | ±2V                        |
    | 102 mV/div - 1 V/div    | ±20 V                      |
    | 1.02 V/div - 10 V/div   | ±200 V                     |
    """
    if scale in available_scales[:8]:  # 500 μV/div to 100 mV/div
        min_val, max_val = -2 * DIAL_PREC_FACT, 2 * DIAL_PREC_FACT
    elif scale in available_scales[8:11]:  # >100 mV/div to 1 V/div
        min_val, max_val = -20 * DIAL_PREC_FACT, 20 * DIAL_PREC_FACT
    elif scale in available_scales[11:]:  # >1 V/div to 10 V/div
        min_val, max_val = -200 * DIAL_PREC_FACT, 200 * DIAL_PREC_FACT
    else:
        logging.debug(f"scale {scale} out of bound")
        return

    ## Test only
    # min_val, max_val = -2 * DIAL_PREC_FACT, 2 * DIAL_PREC_FACT

    pos_dial.setMinimum(min_val)
    pos_dial.setMaximum(max_val)


def adjust_vertical_scale(self, channel):
    """The vertical scale can be adjusted in **Coarse** or **Fine** mode.  
    * **Coarse** adjustment (take counterclockwise as an example): set the vertical scale in 
    1-2-5 step namely 500uV/div, 1 mV/div, 2 mV/div, 5 mV/div, 10 mV/div ...10 V/div. 
    * **Fine** adjustment: further adjust the vertical scale within a relatively smaller range to 
    improve vertical resolution. For example: 2 V/div, 1.98V/div, 1.96V/div, 1.94 V/div ...1 
    V/div. \\
    If the amplitude of the input waveform is a little bit greater than the full scale under the 
    current scale and the amplitude would be a little bit lower if the next scale is used, fine 
    adjustment can be used to improve the amplitude of waveform display to view signal 
    details.

    Press the CH1 button on the front panel; then press the **Adjust** softkey to select the 
    desired mode. Turn the **VERTICAL Variable Knob** to adjust the vertical scale.

    The scale information in the channel label at the right side of the screen will change 
    accordingly during the adjustment. The adjustable range of the vertical scale is related to 
    the probe ratio currently set. By default, the probe attenuation factor is 1X and the 
    adjustable range of the vertical scale is from 500uV/div to 10 V/div."""
    if channel in [1, 2]:
        scale = getattr(self, f"channel{channel}").Vdiv = get_current_scale(self, channel)
        offset_data = getattr(self, f"channel{channel}").Offset
        pos_dial = getattr(self, f"channel{channel}pos_dial")
        set_posdial_limits(scale, pos_dial)
        relim_and_update_chart(self, scale, offset_data, channel)
    else:
        logging.debug(f"channel {channel} not supported")


def adjust_vertical_position(self, channel):
    """Turn the **VERTICAL Position Knob** to adjust the vertical position of the channel
    waveform. Push the knob to set the vertical position of the channel waveform
    to zero.

    During the adjustment, the vertical position information Volts Pos displays at the bottom of
    the screen. The table below shows the range of vertical position according to the volt
    scale.

    | Volt Scale              | Range of Vertical Position |
    |:-----------------------:|:--------------------------:|
    | 500 μV/div - 100 mV/div | ±2V                        |
    | 102 mV/div - 1 V/div    | ±20 V                      |
    | 1.02 V/div - 10 V/div   | ±200 V                     |

    """
    if channel in [1, 2]:
        offset_data = getattr(self, f"channel{channel}").Offset = get_current_offset(self, channel)
        scale = getattr(self, f"channel{channel}").Vdiv
        relim_and_update_chart(self, scale, offset_data, channel)
    else:
        logging.debug(f"channel {channel} not supported")


def specify_channel_coupling(self):
    """Set the coupling mode to filter out the undesired signals. For example, the signal under
    test is a square waveform with DC offset.
    * When the coupling mode set to **DC**: the DC and AC components of the signal under
    test can both pass the channel.
    * When the coupling mode set to **AC**: the DC components of the signal under test are
    blocked.
    * When the coupling mode set to **GND**: the DC and AC components of the signal under
    test are both blocked.

    Press the CH1 button on the front panel; then press the **Coupling** softkey and turn the
    **Universal Knob** to select the desired coupling mode. The default setup is **DC**.

    The current coupling mode is displayed in the channel label at the right side of the screen.
    You can also press the **Coupling** softkey continuously to switch the coupling mode."""
    pass


def specify_bandwidth_limit(self):
    """Set the bandwidth limit to reduce display noise. For example, the signal under test is a
    pulse with high frequency oscillation.
    * When the bandwidth limit set to Full, the high frequency components of the signal
    under test can pass the channel.
    * When the bandwidth limit set to 20M, the high frequency components that exceed 20
    MHz are attenuated.

    Press the CH1 button on the front panel; then press the **BW Limit** softkey to select **Full** or
    **20M**. The default setup is **Full**. When bandwidth limit is enabled, the character **B** will be
    displayed in the channel label at the right side of the screen.

    SDS1000X-E has full BW with all V/div settings including 500uV/div to 2mV/div."""
    pass


def specify_probe_attenuation_factor(self):
    """Set the probe attenuation factor to match the type of the probe that you are using to
    ensure correct vertical readouts.

    Press the CH1 button on the front panel; then press the **Probe** softkey and turn the
    **Universal Knob** to select the desired value and push the knob to confirm. The default
    setup is **1X**.

    The current probe attenuation factor is displayed in the channel label at the right side of
    the screen. You can also press the **Probe** softkey continuously to switch the probe
    attenuation factor.

    The table shows the probe attenuation factor

    | Menu   | Attenuation Factor |
    |:------:|:------------------:|
    | 0.1X   | 0.1 : 1            |
    | 0.2X   | 0.2 : 1            |
    | 0.5X   | 0.5 : 1            |
    | 1X     | 1 : 1              |
    | 2X     | 2 : 1              |
    | ...    | ...                |
    | 5000X  | 5000 : 1           |
    | 10000X | 10000 : 1          |

    """
    pass


def specify_channel_input_impedance(self):
    """The channel input impedance matching gives you the most accurate measurements
    because reflections are minimized along the signal path.
    * Impedance setting to 1MΩ is for use with many passive probes and for general-
    purpose measurements. The higher impedance minimizes the loading effect of the
    oscilloscope on the device under test.

    Press the CH1 button on the front panel; then press the **Impedance** softkey to select the
    desired impedance.

    The current channel input impedance is displayed in the channel label at the right side of
    the screen."""
    pass


def specify_amplitude_unit(self):
    """Select the amplitude display unit for the current channel. The available units are **V** and **A**.
    When the unit is changed, the unit displayed in the channel label will change accordingly.
    1. Press CH1 button on the front panel to enter the CH1 function menu.
    2. Press the **Next Page** softkey to enter the second page of the CH1 function menu.
    3. Press the **Unit** softkey to select the desired unit **V** or **A**.

    The default setup is **V**."""
    pass


def specify_deskew(self):
    """Set the current channel deskew.Adjustable phase difference between the channel, the
    adjusting range of plus or minus 100 ns.
    1. Press CH1 button on the front panel to enter the CH1 function menu.
    2. Press the **Next Page** softkey to enter the second page of the CH1 function menu.
    3. Press the **Deskew** softkey. Then turn the **Universal Knob** to change deskew."""
    pass


def invert_waveform(self):
    """When **Invert** is set to **On**, the voltage values of the displayed waveform are inverted.
    Invert affects how a channel is displayed and it keeps the trigger settings.
    Inverting a channel also changes the result of any math function selected and measure
    function.
    1. Press CH1 button on the front panel to enter the CH1 function menu.
    2. Press the **Next Page** softkey to enter the second page of the CH1 function menu.
    3. Press the **Invert** softkey to turn on or off the invert display."""
    pass
