from signal import signal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, CheckButtons, RadioButtons, TextBox

import generators as gen
from object import Object

signal_type = "sine"
sig_vals = [1.0, 1.0, 0.0, 0.0]
# Po koleji: B, a, kp, Tp, T, x1o, x2o
obj_vals = [1.0, 1.0, 1.0, 1.0, 1.0]

simulated = Object(1.0, 1.0, 1.0, 1.0, 1.0)


def input(t):
    global signal_type
    if signal_type == "sine":
        return gen.harmonic(sig_vals[0], sig_vals[1], t, sig_vals[2])
    elif signal_type == "square":
        return gen.square_wave(sig_vals[0], sig_vals[1], sig_vals[2], t, sig_vals[3])
    elif signal_type == "impulse":
        return gen.impulse(sig_vals[0], sig_vals[1], sig_vals[2], sig_vals[3], t)
    elif signal_type == "triangle":
        return gen.triangle_wave(sig_vals[0], sig_vals[1], t, sig_vals[2])


fig, ax = plt.subplot_mosaic(
    [
        ["main", "object"],
        ["main", "signal"],
        ["main", "sig_param"],
    ],
    width_ratios=[5, 1],
    height_ratios=[6, 3, 3],
    layout="constrained",
)
ax["object"].set_xticks([])
ax["object"].set_yticks([])
ax["sig_param"].set_xticks([])
ax["sig_param"].set_yticks([])

simulated.simulate(10, input)
(l,) = ax["main"].plot(simulated.time, simulated.x1, lw=2)

obj_axes = [
    ax["object"].inset_axes((0.5, 0.8645, 0.40, 0.091)),
    ax["object"].inset_axes((0.5, 0.7280, 0.40, 0.091)),
    ax["object"].inset_axes((0.5, 0.5915, 0.40, 0.091)),
    ax["object"].inset_axes((0.5, 0.4550, 0.40, 0.091)),
    ax["object"].inset_axes((0.5, 0.3185, 0.40, 0.091)),
    ax["object"].inset_axes((0.5, 0.1820, 0.40, 0.091)),
    ax["object"].inset_axes((0.5, 0.0455, 0.40, 0.091)),
]
obj_tbs = [
    TextBox(obj_axes[0], "B", initial="1.0", textalignment="center", label_pad=0.2),
    TextBox(obj_axes[1], "a", initial="1.0", textalignment="center", label_pad=0.2),
    TextBox(obj_axes[2], "$k_p$", initial="1.0", textalignment="center", label_pad=0.2),
    TextBox(obj_axes[3], "$T_p$", initial="1.0", textalignment="center", label_pad=0.2),
    TextBox(obj_axes[4], "T", initial="1.0", textalignment="center", label_pad=0.2),
    TextBox(obj_axes[5], "y(0)", initial="0.0", textalignment="center", label_pad=0.2),
    TextBox(
        obj_axes[6], "y'(0)$", initial="0.0", textalignment="center", label_pad=0.2
    ),
]


def obj_submit(_):
    global simulated
    b = 1.0
    a = 1.0
    kp = 1.0
    tp = 1.0
    t = 1.0
    x1o = 0.0
    x2o = 0.0
    try:
        b = float(obj_tbs[0].text)
        a = float(obj_tbs[1].text)
        kp = float(obj_tbs[2].text)
        tp = float(obj_tbs[3].text)
        t = float(obj_tbs[4].text)
        x1o = float(obj_tbs[5].text)
        x2o = float(obj_tbs[6].text)
    except ValueError:
        pass
    simulated = Object(b, a, kp, tp, t, x1o, x2o)
    simulated.simulate(10, input)
    l.set_xdata(simulated.time)
    l.set_ydata(simulated.x1)
    ax["main"].relim()
    ax["main"].autoscale_view()
    fig.canvas.draw()


for tb in obj_tbs:
    tb.on_submit(obj_submit)

tb_axes = [
    ax["sig_param"].inset_axes((0.60, 0.80, 0.30, 0.15)),
    ax["sig_param"].inset_axes((0.60, 0.55, 0.30, 0.15)),
    ax["sig_param"].inset_axes((0.6, 0.30, 0.30, 0.15)),
    ax["sig_param"].inset_axes((0.6, 0.05, 0.30, 0.15)),
]

sig_tbs = [
    TextBox(
        tb_axes[0], "Amplituda", initial="1.0", textalignment="center", label_pad=0.2
    ),
    TextBox(
        tb_axes[1],
        "Częstotliwość",
        initial="1.0",
        textalignment="center",
        label_pad=0.2,
    ),
    TextBox(
        tb_axes[2], "Offset DC", initial="0.0", textalignment="center", label_pad=0.2
    ),
    TextBox(tb_axes[3], "", initial="", textalignment="center", label_pad=0.2),
]
sig_tbs[3].set_active(False)


def sigparam_submit(_):
    global sig_vals
    try:
        sig_vals[0] = float(sig_tbs[0].text)
        sig_vals[1] = float(sig_tbs[1].text)
        sig_vals[2] = float(sig_tbs[2].text)
        sig_vals[3] = float(sig_tbs[3].text)
    except ValueError:
        pass
    simulated.reset()
    simulated.simulate(10, input)
    l.set_xdata(simulated.time)
    l.set_ydata(simulated.x1)
    ax["main"].relim()
    ax["main"].autoscale_view()
    fig.canvas.draw()


for tb in sig_tbs:
    tb.on_submit(sigparam_submit)

radio = RadioButtons(ax["signal"], ("sine", "square", "impulse", "triangle"))


def sigtype_submit(label):
    global signal_type
    global sig_tbs
    if label == "sine" or label == "triangle":
        sig_tbs[3].set_active(False)
        sig_tbs[3].label.set_text("")
        sig_tbs[3].set_val("")

        sig_tbs[0].label.set_text("Amplituda")
        sig_tbs[0].set_val("1.0")
        sig_tbs[1].label.set_text("Częstotliwość")
        sig_tbs[1].set_val("1.0")
        sig_tbs[2].label.set_text("Offset DC")
        sig_tbs[2].set_val("0.0")
    elif label == "square":
        sig_tbs[3].set_active(True)

        sig_tbs[0].label.set_text("Stan wysoki")
        sig_tbs[0].set_val("1.0")
        sig_tbs[1].label.set_text("Stan niski")
        sig_tbs[1].set_val("0.0")
        sig_tbs[2].label.set_text("Częstotliwość")
        sig_tbs[2].set_val("1.0")
        sig_tbs[3].label.set_text("Wypełnienie")
        sig_tbs[3].set_val("0.5")
    elif label == "impulse":
        sig_tbs[3].set_active(True)

        sig_tbs[0].label.set_text("Stan wysoki")
        sig_tbs[0].set_val("1.0")
        sig_tbs[1].label.set_text("Stan niski")
        sig_tbs[1].set_val("0.0")
        sig_tbs[2].label.set_text("Długość impulsu")
        sig_tbs[2].set_val("0.1")
        sig_tbs[3].label.set_text("Czas startu")
        sig_tbs[3].set_val("1.0")
    signal_type = label
    # Ta funkcja odpala reset plota
    sigparam_submit(label)


radio.on_clicked(sigtype_submit)

plt.show()
