from collections import deque
from decimal import Decimal
import logging
import time
import wave
import debugpy
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from scipy import signal
from scipy.special import erf
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, pyqtSlot


if __name__ != "__main__":
    from front_panel.actions.display import update_plotted_signal
    from systems.horizontal_system.horizontal_functions import (
        get_current_delay,
        get_current_timebase,
    )

    from signal_generator import mem_depth, N_TDIV, N_VDIV
else:
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys

has_trace = hasattr(sys, "gettrace") and sys.gettrace() is not None
has_breakpoint = sys.breakpointhook.__module__ != "sys"
isdebug = has_trace or has_breakpoint

"""Random signals generator here is supposed
to work in a separate process or thread for
the program it is desined for to work smoothly."""

available_waveforms = ["sine", "square", "triangle", "sawtooth", "pulse_train", "pulse_train_conv"]

_dtype = np.float32


def _get_mem_depth_per_channel(active_channels: int) -> int:
    if active_channels:
        return int(mem_depth / active_channels)
    else:
        logging.error("No active channels. Using full memory depth.")
        return int(mem_depth)


def _generate_basepoints(time_range, active_channels: int = 1):
    mem_depth_channel = _get_mem_depth_per_channel(active_channels)
    # Use _dtype instead of float64:
    return np.linspace(
        -float(time_range) / 2,
        float(time_range) / 2,
        mem_depth_channel,
        endpoint=False,
        dtype=_dtype,  # specify lower precision
    )


def _generate_timepoints(timebase: Decimal, active_channels: int, *args, **kwargs):
    """These are timepoints that fit the screen or the oscilloscope's memory buffer"""
    time_range = timebase * Decimal(N_TDIV)

    if "trigger_delay" in kwargs:
        delay: Decimal = kwargs["trigger_delay"]
    else:
        delay = Decimal(0)

    if "previous_timepoints" not in kwargs:
        kwargs["previous_timepoints"] = _generate_basepoints(time_range, active_channels)

    timepoints = _generate_delayed_timepoints(
        kwargs["previous_timepoints"], delay, parent=kwargs.get("parent", None), time_range=time_range
    )
    return timepoints


def _generate_delayed_timepoints(
    previous_timepoints: np.ndarray | None, delay: Decimal, out: np.ndarray = None, **kwargs
) -> np.ndarray:
    """
    Generate a new array of timepoints by applying the trigger delay
    directly on a stable baseline grid. This prevents the delay from being
    applied cumulatively on already delayed timepoints, which can cause the
    displayed data to disappear over successive iterations.

    Parameters:
      time_range (Decimal): The total time window (timebase * N_TDIV).
      mem_depth (int): Number of samples per channel.
      previous_timepoints (np.ndarray): Previously generated timepoints (used
                                          here mainly to deduce dtype).
      delay (Decimal): The trigger delay to apply.

    Returns:
      np.ndarray: New timepoints computed from a baseline grid shifted by delay.
    """
    # Apply the delay shift once, relative to the fixed baseline.
    if "parent" not in kwargs or kwargs["parent"] is None:
        base_t = _generate_basepoints(kwargs["time_range"])
    else:
        base_t = kwargs["parent"].base_t

    # If no preallocated "out" buffer is provided, allocate one.
    if out is None:
        out = np.empty_like(base_t, dtype=_dtype)

    # Update the output array in place by subtracting the delay.
    # Using np.subtract with the `out` parameter avoids a new allocation.
    np.subtract(base_t, float(delay), out=out)

    # Ensure proper data type (if needed, out should already have the correct dtype).
    # If a conversion is needed, you might do this in-place by:
    # out[:] = out.astype(dtype)

    return out


def _generate_random_noise(timepoints, std_dev, out_noise=None, *args, **kwargs):
    rng = np.random.default_rng()
    noise = rng.normal(loc=0.0, scale=std_dev, size=timepoints.shape).astype(_dtype)
    if out_noise is not None:
        out_noise[:] = noise
        return out_noise
    else:
        return noise


# def _generate_sine(freq, phase, timebase, noise_std_dev, active_channels=1, **kwargs):
#     logging.debug(
#         f"generating sine with:\n\t{freq=},\n\t{phase=},\n\t{timebase=},\n\t{noise_std_dev=},\n\t{active_channels=}"
#     )
#     t = getattr(
#         kwargs, "previous_timepoints", _generate_timepoints(timebase, active_channels, **kwargs)
#     )

#     noise = _generate_random_noise(t, noise_std_dev)
#     sine_wave = np.sin(2 * np.pi * freq * t + phase).astype(_dtype)
#     np.add(sine_wave, noise, out=sine_wave)

#     return t, sine_wave, noise

# def _generate_sine(freq, phase, timebase, noise_std_dev, active_channels=1, **kwargs):
#     logging.debug(
#         f"generating sine with:\n\t{freq=},\n\t{phase=},\n\t{timebase=},\n\t{noise_std_dev=},\n\t{active_channels=}"
#     )
#     t = getattr(kwargs, "previous_timepoints", _generate_timepoints(timebase, active_channels, **kwargs))
    
#     noise = _generate_random_noise(t, noise_std_dev)
#     sine_wave = np.sin(2 * np.pi * freq * t + phase).astype(_dtype)
#     np.add(sine_wave, noise, out=sine_wave)

#     return t, sine_wave, noise

def _generate_sine(freq, phase, timebase, noise_std_dev, active_channels=1, out_wfm=None, **kwargs):
    logging.debug(
        f"generating sine with:\n\t{freq=},\n\t{phase=},\n\t{timebase=},\n\t{noise_std_dev=},\n\t{active_channels=}"
    )
    t = kwargs.get("previous_timepoints", _generate_timepoints(timebase, active_channels, **kwargs))
    
    # Generate noise
    noise = _generate_random_noise(t, noise_std_dev)
    
    # Check if out_wfm is provided, otherwise create one
    if out_wfm is None:
        sine_wave = np.sin(2 * np.pi * freq * t + phase).astype(_dtype)
    else:
        # Use the preallocated out_wfm buffer
        np.sin(2 * np.pi * freq * t + phase, out=out_wfm)
        sine_wave = out_wfm

    # Add noise to the sine wave
    np.add(sine_wave, noise, out=sine_wave)

    return t, sine_wave, noise


def _generate_square(freq, phase, timebase, noise_std_dev, active_channels=1, **kwargs):
    logging.debug(
        f"generating square with:\n\t{freq=},\n\t{phase=},\n\t{timebase=},\n\t{noise_std_dev=},\n\t{active_channels=}"
    )
    t = getattr(
        kwargs, "previous_timepoints", _generate_timepoints(timebase, active_channels, **kwargs)
    )

    noise = _generate_random_noise(t, noise_std_dev)
    square_wave = signal.square(2 * np.pi * freq * t + phase).astype(_dtype)
    np.add(square_wave, noise, out=square_wave)

    return t, square_wave, noise


def _generate_sawtooth(freq, phase, timebase, noise_std_dev, active_channels=1, width=1, **kwargs):
    if width != 0.5:
        logging.debug(
            f"generating sawtooth with:\n\t{freq=},\n\t{phase=},\n\t{timebase=},\n\t{noise_std_dev=},\n\t{active_channels=}"
        )
    t = getattr(
        kwargs, "previous_timepoints", _generate_timepoints(timebase, active_channels, **kwargs)
    )
    noise = _generate_random_noise(t, noise_std_dev)
    sawtooth_wave = signal.sawtooth(2 * np.pi * freq * t + phase, width).astype(_dtype)
    np.add(sawtooth_wave, noise, out=sawtooth_wave)

    return t, sawtooth_wave, noise


def _generate_triangle(freq, phase, timebase, noise_std_dev, active_channels=1, **kwargs):
    logging.debug(
        f"generating triangle with:\n\t{freq=},\n\t{phase=},\n\t{timebase=},\n\t{noise_std_dev=},\n\t{active_channels=}"
    )

    return _generate_sawtooth(freq, phase, timebase, noise_std_dev, active_channels, width=0.5)  # type: ignore


def _generate_pulse_train(
    timebase: Decimal,
    noise_std_dev,
    active_channels=1,
    pulse_width=1e-9,
    repetition_rate=1e3,
    dtype=_dtype,
    **kwargs,
):
    """Use this method for small number of pulses"""
    # Determine how many pulses (round up) you need.
    num_pulses = int(np.ceil(float(timebase) * N_TDIV * repetition_rate))

    # Make the number odd so that pulses center nicely around zero.
    if num_pulses % 2 == 0:
        num_pulses += 1

    if num_pulses > 4e5:
        logging.info("Number of pulses exceeds 400k. Switching to convolution method.")
        return _generate_pulse_train_convolution(
            timebase, noise_std_dev, active_channels, pulse_width, repetition_rate, **kwargs
        )

    # Generate the common timepoints and noise.
    t = _generate_timepoints(timebase, active_channels, **kwargs)
    noise = _generate_random_noise(t, noise_std_dev)

    # Initialize the pulse train
    pulse_train = np.zeros_like(t)

    # Sample interval for t
    dt_sample = t[1] - t[0]

    # Define a window that covers ±5*pulse_width
    window_n = int(np.ceil(5 * pulse_width / dt_sample))

    # Create a local time grid for calculating pulse shape
    dt_local = np.linspace(
        -window_n * dt_sample, window_n * dt_sample, 2 * window_n + 1, dtype=_dtype
    )

    # Precompute the pulse shape (envelope and modulation) on this grid
    pulse_shape = np.exp(-(dt_local**2) / (2 * pulse_width**2)) * (
        1 + erf(4.5 * dt_local / (np.sqrt(2) * pulse_width))
    )

    # Precompute pulse centers
    pulse_centers = np.linspace(
        -((num_pulses - 1) / repetition_rate) / 2,
        ((num_pulses - 1) / repetition_rate) / 2,
        num_pulses,
        dtype=_dtype,
    )

    # For each pulse, add the precomputed pulse shape at the correct location
    for center in pulse_centers:
        # Find the index where the pulse center goes
        center_idx = np.searchsorted(t, center)

        # Determine the indices in t that will be updated by this pulse
        idx_start = center_idx - window_n
        idx_end = center_idx + window_n + 1  # +1 because slicing excludes the end

        # Adjust in case the window goes out of bounds (pulse might not fit in the data)
        valid_start = max(idx_start, 0)
        valid_end = min(idx_end, len(t))

        # Determine the corresponding slice in t of the precomputed pulse shape
        pulse_shape_start = valid_start - idx_start
        pulse_shape_end = pulse_shape_start + (valid_end - valid_start)

        pulse_train[valid_start:valid_end] += pulse_shape[pulse_shape_start:pulse_shape_end]

    # Normalize the pulse train, ensuring the peak amplitude is 1.
    pulse_train /= np.max(np.abs(pulse_train))

    return t, pulse_train + noise, noise


def _generate_pulse_train_convolution(
    timebase: Decimal,
    noise_std_dev,
    active_channels=1,
    pulse_width=1e-9,
    repetition_rate=1e3,
    dtype=_dtype,
    **kwargs,
):
    """Use this method for large number of pulses"""
    # Determine how many pulses to create.
    num_pulses = int(np.ceil(float(timebase) * N_TDIV * repetition_rate))
    # Make it odd to center nicely around zero.
    if num_pulses % 2 == 0:
        num_pulses += 1

    # Generate the global time array and noise.
    t = _generate_timepoints(timebase, active_channels, **kwargs)
    noise = _generate_random_noise(t, noise_std_dev)

    # Compute the sample spacing.
    dt_sample = t[1] - t[0]

    # Precompute the canonical pulse shape.
    window_n = int(np.ceil(5 * pulse_width / dt_sample))

    # Create a local time grid for one pulse.
    dt_local = np.linspace(
        -window_n * dt_sample, window_n * dt_sample, 2 * window_n + 1, dtype=_dtype
    )
    pulse_shape = np.exp(-(dt_local**2) / (2 * pulse_width**2)) * (
        1 + erf(4.5 * dt_local / (np.sqrt(2) * pulse_width))
    )

    # Create an impulse train: an array of zeros with ones (or weights) at pulse center indices.
    impulse_train = np.zeros_like(t)

    # Compute pulse centers in time.
    pulse_centers = np.linspace(
        -((num_pulses - 1) / repetition_rate) / 2,
        ((num_pulses - 1) / repetition_rate) / 2,
        num_pulses,
        dtype=_dtype,
    )

    # Convert pulse centers to indices in t
    # Ensure that every pulse center corresponds to a valid index in t
    pulse_indices = np.searchsorted(t, pulse_centers, side="left")
    pulse_indices = np.clip(pulse_indices, 0, len(t) - 1)

    # Use np.bincount to add up impulses (in case multiple pulses fall in the same index)
    impulse_train = np.bincount(pulse_indices, minlength=len(t))

    # Convolve the impulse train with the precomputed pulse shape.
    # fftconvolve is very efficient for large arrays.
    pulse_train = signal.fftconvolve(impulse_train, pulse_shape, mode="same")

    # Normalize so that the peak is at 1
    pulse_train /= np.max(np.abs(pulse_train))

    return t, pulse_train + noise, noise


def _calculate_rise_time(signal, t):
    """Calculate rise time from 10% to 90% of the signal amplitude"""
    # Find the maximum value of the signal
    max_value = np.max(signal)

    # Find the 10% and 90% values of the maximum
    value_10 = 0.1 * max_value
    value_90 = 0.9 * max_value

    # Find the indices where the signal crosses the 10% and 90% values
    index_10 = np.where(signal >= value_10)[0][0]  # First index where signal is >= 10%
    index_90 = np.where(signal >= value_90)[0][0]  # First index where signal is >= 90%

    # Get the corresponding x-values (time values)
    x_10 = t[index_10]
    x_90 = t[index_90]

    # Calculate delta x
    delta_x = x_90 - x_10

    return delta_x * 1e9, x_10, x_90


def get_waveform(*args, out_t=None, out_wfm=None, out_noise=None, **kwargs):
    if "waveform" not in kwargs:
        logging.error("Provide waveform type.")
        return

    if "active_channels" in kwargs:
        if not kwargs["active_channels"]:
            logging.error("No active channels.")
            return

    # if connector is unplugged, return noise only
    if "connector_state" not in kwargs or not kwargs["connector_state"]:
        # Update the preallocated timepoints buffer if provided.
        if out_t is not None:
            out_t[:] = _generate_timepoints(*args, **kwargs)
        else:
            out_t = _generate_timepoints(*args, **kwargs)
        
        # Generate noise in place: check if an output noise buffer was provided.
        if "noise_std_dev" in kwargs:
            std_dev = kwargs["noise_std_dev"]
            # Check if an out_noise buffer is provided.
            if out_noise is not None:
                _generate_random_noise(out_t, std_dev, out_noise=out_noise, *args, **kwargs)
            else:
                out_noise = _generate_random_noise(out_t, std_dev, *args, **kwargs)
            
            # For a connector-unplugged state, you might want to use the noise as both waveform and noise.
            return out_t, out_noise, out_noise
        else:
            return out_t, np.zeros_like(out_t), np.zeros_like(out_t)

    waveform = kwargs.get("waveform")
    match waveform:
        case "sine":
            return _generate_sine(
                *args, out_t=out_t, out_wfm=out_wfm, out_noise=out_noise, **kwargs
            )
        case "square":
            return _generate_square(
                *args, out_t=out_t, out_wfm=out_wfm, out_noise=out_noise, **kwargs
            )
        case "triangle":
            return _generate_triangle(
                *args, out_t=out_t, out_wfm=out_wfm, out_noise=out_noise, **kwargs
            )
        case "sawtooth":
            return _generate_sawtooth(
                *args, out_t=out_t, out_wfm=out_wfm, out_noise=out_noise, **kwargs
            )
        case "pulse_train":
            return _generate_pulse_train(
                *args, out_t=out_t, out_wfm=out_wfm, out_noise=out_noise, **kwargs
            )
        case "pulse_train_conv":
            return _generate_pulse_train_convolution(
                *args, out_t=out_t, out_wfm=out_wfm, out_noise=out_noise, **kwargs
            )
        case _:
            logging.debug("Unsupported waveform.")
            return None


def _re_noise(t, wfm, noise, noise_std_dev):
    """Use to refresh noise data - simulate "constantly" incoming signals"""

    new_noise = _generate_random_noise(t, noise_std_dev)

    # Replace the old noise with new one (in-place to save RAM)
    np.subtract(wfm, noise, out=wfm)
    np.add(wfm, new_noise, out=wfm)

    return t, wfm, new_noise


class SignalManager:
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.running_threads = []

    def start_signal_generator(self, channel: int, connector_state: bool):
        if channel == 1:
            # Ensure the previous thread is properly finished
            if hasattr(self, "channel1_thread") and self.channel1_thread is not None:
                self.stop_signal_generator(channel)
            if hasattr(self, "channel1_generator") and self.channel1_generator is not None:
                self.stop_signal_generator(channel)
            # Define worker thread
            self.channel1_thread = QThread()
            self.running_threads.append(self.channel1_thread)
            self.channel1_generator = SignalGenerator(self.parent, channel, connector_state)
            self.channel1_generator.moveToThread(self.channel1_thread)
            self.channel1_thread.started.connect(self.channel1_generator.run)
            self.channel1_generator.finished.connect(self.channel1_thread.quit)
            self.channel1_generator.finished.connect(self.channel1_generator.deleteLater)
            self.channel1_thread.finished.connect(self.channel1_thread.deleteLater)
            self.channel1_generator.progress.connect(self._reportProgress)
            self.parent.timebase_selected.connect(
                lambda tb: self.channel1_generator.update_timebase(tb)  # type: ignore
            )
            self.parent.delay_selected.connect(
                lambda delay: self.channel1_generator.update_trigger_delay(delay)  # type: ignore
            )
            self.parent.connector1_toggled.connect(
                lambda state: self.channel1_generator.update_connector_state(state)  # type: ignore
            )
            self.channel1_thread.start()

        elif channel == 2:
            # Ensure the previous thread is properly finished
            if hasattr(self, "channel2_thread") and self.channel2_thread is not None:
                self.stop_signal_generator(channel)
            if hasattr(self, "channel2_generator") and self.channel2_generator is not None:
                self.stop_signal_generator(channel)
            # Define worker thread
            self.channel2_thread = QThread()
            self.running_threads.append(self.channel1_thread)
            self.channel2_generator = SignalGenerator(self.parent, channel, connector_state)
            self.channel2_generator.moveToThread(self.channel2_thread)
            self.channel2_thread.started.connect(self.channel2_generator.run)
            self.channel2_generator.finished.connect(self.channel2_thread.quit)
            self.channel2_generator.finished.connect(self.channel2_generator.deleteLater)
            self.channel2_thread.finished.connect(self.channel2_thread.deleteLater)
            self.channel2_generator.progress.connect(self._reportProgress)
            self.parent.timebase_selected.connect(
                lambda tb: self.channel2_generator.update_timebase(tb)  # type: ignore
            )
            self.parent.delay_selected.connect(
                lambda delay: self.channel2_generator.update_trigger_delay(delay)  # type: ignore
            )
            self.parent.connector2_toggled.connect(
                lambda state: self.channel2_generator.update_connector_state(state)  # type: ignore
            )
            self.channel2_thread.start()

        else:
            logging.debug("Invalid channel number. Accepts 1 and 2 only.")

    def stop_signal_generator(self, channel):
        if (
            channel == 1
            and self.channel1_thread is not None
            and self.channel1_generator is not None
            and self.channel1_generator.is_running()
        ):
            self.channel1_generator.stop()
            self.channel1_thread.quit()
            self.channel1_thread.wait()
            self.channel1_thread = None
            self.channel1_generator = None
            print("Thread for channel 1 quitted.")
        elif (
            channel == 2
            and self.channel2_thread is not None
            and self.channel2_generator is not None
            and self.channel2_generator.is_running()
        ):
            self.channel2_generator.stop()
            self.channel2_thread.quit()
            self.channel2_thread.wait()
            self.channel2_thread = None
            self.channel2_generator = None
            print("Thread for channel 2 quitted.")
        else:
            logging.debug("Invalid channel number. Accepts 1 and 2 only.")

    def _reportProgress(self, channel, t, wfm):
        """This function will be responsible for plotting updated signal."""
        if self.parent:
            update_plotted_signal(self.parent, channel, t, wfm)


class SignalGenerator(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, object, object)

    def __init__(self, parent, channel, connector_state, *args, waveform="sine", **kwargs):
        super().__init__()
        self.parent = parent
        self.running = True
        self.waveform = waveform
        self.channel = channel
        self.connector_state = connector_state
        self.timebase: Decimal = get_current_timebase(self.parent)
        self.trigger_delay: Decimal = get_current_delay(self.parent, self.timebase)
        self.base_t = _generate_basepoints(self.timebase * Decimal(N_TDIV))

        # BUFFERING THE DATA ACQUISITION AND UPDATE
        self.t_buffer = np.empty_like(self.base_t)
        self.wfm_buffer = np.empty_like(self.base_t)
        self.noise_buffer = np.empty_like(self.base_t)

        self.t = self.t_buffer
        self.wfm = self.wfm_buffer
        self.noise = self.noise_buffer
        # END OF BUFFER DEFINITIONS

        if "noise_std_dev" in kwargs:
            self.noise_std_dev = kwargs["noise_std_dev"]

        # Create a queue to store update events (can store parameter names or even full state snapshots)
        self.update_queue = deque()

        # Create a debouncing QTimer for processing GUI events.
        self.update_timer = QTimer()
        self.update_timer.setInterval(
            100
        )  # 100 ms debounce interval is enough to process the timepoints generation (30-70 ms)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.perform_update)

        # Create a QTimer for throttling the update calls.
        # self.throttle_timer = QTimer()
        # self.throttle_timer.setInterval(16)  # ~16 ms yields roughly 60 updates per second.
        # self.throttle_timer.timeout.connect(self.perform_update)
        # self.throttle_timer.start()

        # Create a flag to (dis)allow processing the updates
        self._update_pending = False

    @pyqtSlot(Decimal)
    def update_timebase(self, timebase: Decimal):
        """Receive signal that the timebase changed."""
        # Enqueue the update
        self.update_queue.append(("timebase", timebase))
        # Update the current state and recalculate base timepoints.
        self.timebase = timebase
        self.base_t = _generate_basepoints(self.timebase * Decimal(N_TDIV))
        # Re(start) the timer for debounce (required for updating the waveform)
        self.update_timer.start()

    @pyqtSlot(bool)
    def update_connector_state(self, connector_state: bool):
        """Receive signal that the connector is (un)plugged."""
        # Update the current state
        self.connector_state = connector_state
        # Re(start) the timer for debounce (required for updating the waveform)
        self.update_timer.start()

    @pyqtSlot(bool)
    def update_trigger_delay(self, delay: Decimal):
        # Enqueue the update
        self.update_queue.append(("trigger_delay", delay))
        # Update the current state
        self.trigger_delay = delay
        # Re(start) the timer for debounce (required for updating the waveform)
        self.update_timer.start()

    def perform_update(self):
        """Controls the flag for whether run() should perform waveform update"""
        self._update_pending = True

    def initialize_waveform(self, *args, **kwargs):
        result = get_waveform(
            *args,
            out_t=self.t_buffer,
            out_wfm=self.wfm_buffer,
            out_noise=self.noise_buffer,
            **kwargs,
        )
        if not result:
            print("result is None")
            return

        self.t[:] = self.t_buffer
        self.wfm[:] = self.wfm_buffer
        self.noise[:] = self.noise_buffer
    
    def run(self):
        """Generate/update the signal"""
        if isdebug:
            debugpy.debug_this_thread()
        # TEST VALUES
        self.noise_std_dev = 0.01
        phase = 0
        if self.channel == 2:
            phase = np.pi / 2
        # END OF TEST VALUES
        
        print("Initializing waveform")
        self.initialize_waveform(
            waveform=self.waveform,
            connector_state=self.connector_state,
            trigger_delay=self.trigger_delay,
            previous_timepoints=self.base_t,
            freq=50e6,
            phase=phase,
            timebase=self.timebase,
            noise_std_dev=self.noise_std_dev,
            active_channels=1,
            pulse_width=1e-9,
            repetition_rate=88e6,
            parent=self,
        )
        print("Waveform initialized")
        
        while self.running:
            if not self.running:
                break

            if self._update_pending:
                # Allowed only after the debounce period has expired

                # Only the final state matters, so we simply clear the queue.
                while self.update_queue:
                    _ = self.update_queue.popleft()
                    # if update_type == "timebase":
                    #     # Update timebase-specific behavior here.
                    #     self.timebase = value
                    #     self.base_t = _generate_basepoints(self.timebase * Decimal(N_TDIV))
                    # elif update_type == "trigger_delay":
                    #     self.trigger_delay = value

                result = get_waveform(
                    waveform=self.waveform,
                    connector_state=self.connector_state,
                    trigger_delay=self.trigger_delay,
                    previous_timepoints=self.base_t,
                    freq=50e6,
                    phase=phase,
                    timebase=self.timebase,
                    noise_std_dev=self.noise_std_dev,
                    active_channels=1,
                    pulse_width=1e-9,
                    repetition_rate=88e6,
                    parent=self,
                    out_t=self.t_buffer,
                    out_wfm=self.wfm_buffer,
                    out_noise=self.noise_buffer,
                )
                if not result:
                    print("result is None")
                    return

                # In-place update
                self.t[:] = self.t_buffer
                self.wfm[:] = self.wfm_buffer
                self.noise[:] = self.noise_buffer

                # Reset _update_pending flag
                self._update_pending = False

            # if display is idly showing signal (no gui changes), update only noise
            else:
                self.t, self.wfm, self.noise = _re_noise(
                    self.t, self.wfm, self.noise, self.noise_std_dev
                )

            self.progress.emit(self.channel, self.t, self.wfm)

        self.finished.emit()
        self.stop()

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running


if __name__ == "__main__":
    # test
    f = 50E6
    tb = Decimal(20E-9)  # at 1E-2 1ns pulses at 88MHz repetition rate are gone! Artifacts show up to the rightmost peak
    mem_depth = 1400  # number of datapoints in memory
    N_TDIV = 10  # number of horizontal divisions
    N_VDIV = 10  # number of vertical divisions
    
    for w in available_waveforms:
        if w == "sine":
            tic = time.time_ns()
            result = get_waveform(waveform=w, freq=f, phase=0, timebase=tb, noise_std_dev=.0, active_channels=1, pulse_width=1E-9, repetition_rate=88E6)
            toc = time.time_ns()
            print(f"Calculation took {(toc-tic)*1E-6} ms")
            if result:
                t, wfm, noise = result
                line, = plt.plot(t, wfm, lw=1, antialiased=True)
                toc2 = time.time_ns()
                print(f"Plotting took {(toc2-toc)*1E-6} ms")
                t, wfm, noise = _re_noise(*result, noise_std_dev=.01)
                toc3 = time.time_ns()
                print(f"Reapplying noise took {(toc3-toc2)*1E-6} ms")
                line.set_ydata(wfm)
                plt.draw()
                toc4 = time.time_ns()
                print(f"Re-plotting took {(toc4-toc3)*1E-6} ms")

    plt.show()
    
    

    # freq = 0.05
    # phase = 0
    # # all in nanoseconds:
    # tb = Decimal(20)
    # delay = Decimal(0)
    # tr = tb * Decimal(N_TDIV)
    # i = 0
    # print(f"{i}: generating timepoints with {delay}")
    # tp = _generate_timepoints(
    #     timebase=tb,
    #     active_channels=1,
    #     trigger_delay=delay,
    #     previous_timepoints=None,
    #     time_range=tr,
    #     parent=None,
    # )

    # colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    # for trigger_delay in [-5, 0, 5]:
    #     print(f"{i+1}: generating timepoints with {trigger_delay}")
    #     tp = _generate_timepoints(
    #         timebase=tb,
    #         active_channels=1,
    #         trigger_delay=Decimal(trigger_delay),
    #         previous_timepoints=tp,
    #         time_range=tr,
    #         parent=None,
    #     )

    #     sine_wave = np.sin(2 * np.pi * freq * tp + phase)

    #     xlims = (float(-tb * N_TDIV / 2 - trigger_delay), float(tb * N_TDIV / 2 - trigger_delay))
    #     plt.axvline(xlims[0], color=colors[i])
    #     plt.axvline(xlims[1], color=colors[i])

    #     plt.plot(tp, sine_wave + i, label=f"{trigger_delay, xlims, min(tp), max(tp)}")

    #     i += 1

    # plt.xlim(-115, 115)
    # plt.legend(loc="lower left")
    # plt.show()
