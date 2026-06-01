from signal import signal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons, TextBox

import generators as gen
from object import Object

signal_type = "sine"
sig_vals = [1.0, 1.0, 0.0, 0.0]
simulated = Object(1.0, 1.0, 1.0, 1.0, 1.0)

INITIAL_SIM_TIME = 0.0
ANIMATION_FREQ_HZ = 60.0
ANIMATION_SPEED = 1.0
SIM_EXTEND_CHUNK = 5.0
VIEW_WINDOW = 15.0
anim_time = 0.0
is_paused = False

INITIAL_PRE_SIM_TIME = max(0.1, INITIAL_SIM_TIME)


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

simulated.simulate(INITIAL_PRE_SIM_TIME, input)
(l1,) = ax["main"].plot(
    simulated.time[:1],
    simulated.r[:1],
    lw=2,
    color="red",
    alpha=0.3,
    label="r(t)",
)
(l0,) = ax["main"].plot(
    simulated.time[:1], simulated.x1[:1], lw=2, color="black", label="y(t)"
)

time_cursor = ax["main"].axvline(0, color="black", lw=1, alpha=0.3)


def set_view_window(t):
    start = max(0.0, float(t) - VIEW_WINDOW)
    ax["main"].set_xlim(start, start + VIEW_WINDOW)


def update_y_limits():
    global signal_type
    if signal_type != "impulse":
        y_min = float(min(simulated.x1.min(), simulated.r.min()))
        y_max = float(max(simulated.x1.max(), simulated.r.max()))
    else:
        y_min = float(simulated.x1.min())
        y_max = float(simulated.x1.max())
    pad = 0.1 * (y_max - y_min) if y_max > y_min else 1.0
    ax["main"].set_ylim(y_min - pad, y_max + pad)


def update_plot_at_time(t):
    global anim_time
    anim_time = max(0.0, min(float(t), float(simulated.time[-1])))
    idx = np.searchsorted(simulated.time, anim_time, side="right")
    if idx < 1:
        idx = 1
    l1.set_xdata(simulated.time[:idx])
    l1.set_ydata(simulated.r[:idx])
    l0.set_xdata(simulated.time[:idx])
    l0.set_ydata(simulated.x1[:idx])
    t_vis = simulated.time[idx - 1]
    time_cursor.set_xdata([t_vis, t_vis])


def reset_animation():
    global anim_time
    anim_time = float(simulated.time[-1])
    update_plot_at_time(anim_time)
    update_y_limits()
    set_view_window(anim_time)
    fig.canvas.draw_idle()


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
    TextBox(obj_axes[6], "y'(0)", initial="0.0", textalignment="center", label_pad=0.2),
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
    simulated.simulate(INITIAL_PRE_SIM_TIME, input)
    reset_animation()


for tb in obj_tbs:
    tb.on_submit(obj_submit)

tb_axes = [
    ax["sig_param"].inset_axes((0.6, 0.85, 0.3, 0.1)),
    ax["sig_param"].inset_axes((0.6, 0.65, 0.3, 0.1)),
    ax["sig_param"].inset_axes((0.6, 0.45, 0.3, 0.1)),
    ax["sig_param"].inset_axes((0.6, 0.25, 0.3, 0.1)),
    ax["sig_param"].inset_axes((0.6, 0.05, 0.3, 0.1)),
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

pause_button = Button(tb_axes[4], "Pause")


def toggle_pause(_):
    global is_paused
    is_paused = not is_paused
    pause_button.label.set_text("Play" if is_paused else "Pause")
    fig.canvas.draw_idle()


pause_button.on_clicked(toggle_pause)


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
    simulated.simulate(INITIAL_PRE_SIM_TIME, input)
    reset_animation()


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


def animate(_):
    global anim_time
    if len(simulated.time) < 2:
        return (l0, time_cursor)

    if not is_paused:
        anim_time += (1.0 / ANIMATION_FREQ_HZ) * ANIMATION_SPEED * 10.0
        if anim_time > simulated.time[-1]:
            simulated.simulate(simulated.time[-1] + SIM_EXTEND_CHUNK, input)
            update_y_limits()

    update_plot_at_time(anim_time)

    x_min, x_max = ax["main"].get_xlim()
    if anim_time > x_max - 0.1 * VIEW_WINDOW and not is_paused:
        new_min = max(0.0, anim_time - 0.9 * VIEW_WINDOW)
        new_max = new_min + VIEW_WINDOW
        ax["main"].set_xlim(new_min, new_max)

    return (l0, time_cursor)


radio.on_clicked(sigtype_submit)

reset_animation()

anim = FuncAnimation(
    fig,
    animate,
    interval=1000.0 / ANIMATION_FREQ_HZ,
    blit=False,
    save_count=200,
)

plt.show()
