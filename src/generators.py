import numpy as np


def harmonic(amplitude, frequency, time, dc_offset=0.0):
    return 0.5 * amplitude * np.sin(2 * np.pi * frequency * time) + dc_offset


def square_wave(high_state, low_state, frequency, time, fill=0.5):
    period = 1 / frequency
    if (time % period) <= fill * period:
        return high_state
    else:
        return low_state


def impulse(high_state, len, start_t, time, dc_offset=0.0):
    if start_t <= time <= start_t + len:
        return high_state + dc_offset
    else:
        return dc_offset


def triangle_wave(amplitude, frequency, time, dc_offset=0.0):
    period = 1 / frequency
    t = (time % period) / period
    if t < 0.25:
        return 2 * amplitude * t / period + dc_offset
    elif t < 0.75:
        return -2 * amplitude * (t / period - 0.5) + dc_offset
    else:
        return 2 * amplitude * (t / period - 1) + dc_offset
