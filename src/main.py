import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Frame, Button, TOP, Label, LEFT, S, Scale, HORIZONTAL, Entry, E, W
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re


def liang_barsky(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    p = [x1 - x2, x2 - x1, y1 - y2, y2 - y1]
    q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
    t_in, t_out = 0, 1
    visible = True
    for i in range(4):
        if p[i] < 0:
            t_in = max(t_in, q[i] / p[i])
        if p[i] > 0:
            t_out = min(t_out, q[i] / p[i])
        if p[i] == 0:
            if q[i] < 0:
                visible = False
                break
            if q[i] >= 0:
                continue
    x_in = x1 + t_in * (x2 - x1)
    y_in = y1 + t_in * (y2 - y1)
    x_out = x1 + t_out * (x2 - x1)
    y_out = y1 + t_out * (y2 - y1)
    if t_in > t_out:
        visible = False
    return visible, x_in, y_in, x_out, y_out


def cyrus_beck(x1, y1, x2, y2, polygon_x_arr, polygon_y_arr):
    n = len(polygon_x_arr)
    line_dx = x2 - x1
    line_dy = y2 - y1
    t_in = [0]
    t_out = [1]
    for i in range(n):
        i1 = i
        i2 = (i + 1) % n
        dx = polygon_x_arr[i2] - polygon_x_arr[i1]
        dy = polygon_y_arr[i2] - polygon_y_arr[i1]

        normal_segment_scalar_product = dy * line_dx - dx * line_dy
        if normal_segment_scalar_product == 0:
            if dy * (x1 - polygon_x_arr[i1]) - dx * (y1 - polygon_y_arr[i1]) < 0:
                return False, None, None, None, None
            else:
                continue

        x_center = (polygon_x_arr[i2] + polygon_x_arr[i1]) / 2
        y_center = (polygon_y_arr[i2] + polygon_y_arr[i1]) / 2
        t = (-dy * (x1 - x_center) + dx * (y1 - y_center)) / (dy * line_dx - dx * line_dy)

        if normal_segment_scalar_product > 0:
            t_in.append(t)
        if normal_segment_scalar_product < 0:
            t_out.append(t)

    max_t_in = max(t_in)
    min_t_out = min(t_out)
    visible = True
    if max_t_in > min_t_out:
        visible = False

    return visible, x1 + max_t_in * line_dx, y1 + max_t_in * line_dy, x1 + min_t_out * line_dx, y1 + min_t_out * line_dy


def draw_rectangle(ax, x_min, y_min, x_max, y_max):
    line_width = 1.5
    ax.plot([x_min, x_max], [y_min, y_min], c='green', ls='-', lw=line_width, alpha=1)
    ax.plot([x_min, x_max], [y_max, y_max], c='green', ls='-', lw=line_width, alpha=1)
    ax.plot([x_min, x_min], [y_min, y_max], c='green', ls='-', lw=line_width, alpha=1)
    ax.plot([x_max, x_max], [y_min, y_max], c='green', ls='-', lw=line_width, alpha=1)


def draw_polygon(ax, polygon_x_arr, polygon_y_arr):
    polygon_x_arr.append(polygon_x_arr[0])
    polygon_y_arr.append(polygon_y_arr[0])
    ax.plot(polygon_x_arr, polygon_y_arr, c='green', ls='-', lw=1.5, alpha=1)


def draw_lines(ax, x1_arr, y1_arr, x2_arr, y2_arr, color):
    for i in range(len(x1_arr)):
        ax.plot([x1_arr[i], x2_arr[i]], [y1_arr[i], y2_arr[i]], c=color, ls='-', lw=1, alpha=1)


def draw_coordinates(ax):
    # length of axes and the space between tick labels
    global xmin, xmax, ymin, ymax
    global ticks_frequency

    # Set identical scales for both axes
    ax.set(xlim=(xmin - 1, xmax + 1), ylim=(ymin - 1, ymax + 1), aspect='equal')

    # Set bottom and left spines as x and y axes of coordinate system
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_position('zero')

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Create 'x' and 'y' labels placed at the end of the axes
    ax.set_xlabel('x', size=14, labelpad=-24, x=1.03)
    ax.set_ylabel('y', size=14, labelpad=-21, y=1.02, rotation=0)

    # Create custom major ticks to determine position of tick labels
    x_ticks = np.arange(xmin, xmax + 1, ticks_frequency)
    y_ticks = np.arange(ymin, ymax + 1, ticks_frequency)
    ax.set_xticks(x_ticks[x_ticks != 0])
    ax.set_yticks(y_ticks[y_ticks != 0])

    # Create minor ticks placed at each integer to enable drawing of minor grid
    # lines: note that this has no effect in this example with ticks_frequency=1
    ax.set_xticks(np.arange(xmin, xmax + 1), minor=True)
    ax.set_yticks(np.arange(ymin, ymax + 1), minor=True)

    # Draw major and minor grid lines
    ax.grid(which='major', color='grey', linewidth=1, linestyle='-', alpha=0.2)

    # Draw arrows
    arrow_fmt = dict(markersize=4, color='black', clip_on=False)
    ax.plot((1), (0), marker='>', transform=ax.get_yaxis_transform(), **arrow_fmt)
    ax.plot((0), (1), marker='^', transform=ax.get_xaxis_transform(), **arrow_fmt)

def init_canvas():
    global canvas, canvas_frame, canvas_size
    fig, ax = plt.subplots(figsize=(10, 10))
    draw_coordinates(ax)
    draw_rectangle(ax, rect_x1, rect_y1, rect_x2, rect_y2)
    draw_lines(ax, x1_arr, y1_arr, x2_arr, y2_arr, 'black')
    if canvas:
        canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().configure(width=canvas_size, height=canvas_size)
    canvas.get_tk_widget().pack(side=TOP, fill=None, expand=0)


def on_liang_barsky_btn_click():
    global canvas, canvas_frame, canvas_size
    global rect_x1, rect_y1, rect_x2, rect_y2
    global x1_arr, y1_arr, x2_arr, y2_arr
    fig, ax = plt.subplots(figsize=(10, 10))
    draw_coordinates(ax)
    draw_rectangle(ax, rect_x1, rect_y1, rect_x2, rect_y2)
    draw_lines(ax, x1_arr, y1_arr, x2_arr, y2_arr, 'black')
    for i in range(lines_num):
        visible, x1, y1, x2, y2 = liang_barsky(x1_arr[i], y1_arr[i], x2_arr[i], y2_arr[i], rect_x1, rect_y1, rect_x2,
                                               rect_y2)
        if visible:
            ax.plot([x1, x2], [y1, y2], c='red', ls='-', lw=1.5, alpha=1)
    if canvas:
        canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().configure(width=canvas_size, height=canvas_size)
    canvas.get_tk_widget().pack(side=TOP, fill=None, expand=0)


def on_cyrus_beck_btn_click():
    global canvas, canvas_frame, canvas_size
    global polygon_x_arr, polygon_y_arr
    global x1_arr, y1_arr, x2_arr, y2_arr
    global lines_num
    fig, ax = plt.subplots(figsize=(10, 10))
    draw_coordinates(ax)
    draw_polygon(ax, polygon_x_arr, polygon_y_arr)
    draw_lines(ax, x1_arr, y1_arr, x2_arr, y2_arr, 'black')
    for i in range(lines_num):
        visible, x1, y1, x2, y2 = cyrus_beck(x1_arr[i], y1_arr[i], x2_arr[i], y2_arr[i], polygon_x_arr, polygon_y_arr)
        if visible:
            ax.plot([x1, x2], [y1, y2], c='red', ls='-', lw=1.5, alpha=1)
    if canvas:
        canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().configure(width=canvas_size, height=canvas_size)
    canvas.get_tk_widget().pack(side=TOP, fill=None, expand=0)


def check_input(value, widget_name):
    global window
    widget = window.nametowidget(widget_name)
    result = re.match("^(-?[1-9]\d*)*$", value) is not None
    global invalid_inputs_num
    if not result:
        widget.config(highlightthickness=1, highlightbackground="red")
        invalid_inputs_num += 1
    else:
        widget.config(highlightthickness=0)
        invalid_inputs_num -= 1
    return result


def update_grid_params():
    if invalid_inputs_num > 0:
        return
    global xmin, ymin, xmax, ymax, ticks_frequency
    global min_x_entry, min_y_entry, max_x_entry, max_y_entry, tick_entry
    if (min_x_entry.get() != ""):
        xmin = int(min_x_entry.get())
    if (min_y_entry.get() != ""):
        ymin = int(min_y_entry.get())
    if (max_x_entry.get() != ""):
        xmax = int(max_x_entry.get())
    if (max_y_entry.get() != ""):
        ymax = int(max_y_entry.get())
    if (tick_entry.get() != ""):
        ticks_frequency = int(tick_entry.get())


# ---------------------- read lines, rectangle and polygon from file ----------------------
input_file = open("input4.txt", "r")
lines_num = int(input_file.readline())

x1_arr = [None] * lines_num
y1_arr = [None] * lines_num
x2_arr = [None] * lines_num
y2_arr = [None] * lines_num

for i in range(lines_num):
    str = input_file.readline().strip()
    x1_arr[i], y1_arr[i], x2_arr[i], y2_arr[i] = [float(x) for x in str.split()]

str = input_file.readline().strip()
rect_x1, rect_y1, rect_x2, rect_y2 = [float(x) for x in str.split()]

vertex_num = int(input_file.readline())
polygon_x_arr = [None] * vertex_num
polygon_y_arr = [None] * vertex_num
for i in range(vertex_num):
    str = input_file.readline().strip()
    polygon_x_arr[i], polygon_y_arr[i] = [float(x) for x in str.split()]

input_file.close()

# ---------------------- set up window  ----------------------

window = Tk()
window.title('Lab 5. Clipping algorithms')
window.geometry("1200x720")

canvas_size = 700
canvas_frame = Frame(width=canvas_size, height=canvas_size)
canvas_frame.grid(row=1, column=1)
canvas = None

buttons_frame = Frame()
buttons_frame.grid(row=1, column=2, padx=30)

btn_width = 40
liang_barsky_btn = Button(master=buttons_frame, text="Алгоритм Лианга-Барски", width=btn_width,
                          command=on_liang_barsky_btn_click)
liang_barsky_btn.grid(row=4, column=0, pady=20)
cyrus_beck_btn = Button(master=buttons_frame, text="Алгоритм Кируса-Бека", width=btn_width,
                        command=on_cyrus_beck_btn_click)
cyrus_beck_btn.grid(row=5, column=0, pady=10)

plot_params_frame = Frame(master=buttons_frame)
plot_params_frame.grid(row=1, column=0)
label_width = 6
entry_width = 16

check = (window.register(check_input), "%P", "%W")
invalid_inputs_num = 0

xmin, xmax, ymin, ymax = -10, 10, -10, 10
ticks_frequency = 1

frame = Frame(master=plot_params_frame)
frame.grid(row=0, column=0)
label = Label(master=frame, text="Xmin: ", font=("Arial", 12), width=label_width, anchor=W)
label.pack(side=LEFT, anchor=S)
# start_x_slider = Scale(master=frame, from_=-80, to=80, orient=HORIZONTAL, font=("Arial", 10), length=160)
# start_x_slider.set(1)
# start_x_slider.pack()
min_x_entry = Entry(master=frame, validate="focusout", validatecommand=check, width=entry_width)
min_x_entry.pack()

frame = Frame(master=plot_params_frame)
frame.grid(row=0, column=1)
label = Label(master=frame, text="Ymin: ", font=("Arial", 12), width=label_width, anchor=W)
label.pack(side=LEFT, anchor=S)
min_y_entry = Entry(master=frame, validate="focusout", validatecommand=check, width=entry_width)
min_y_entry.pack()

frame = Frame(master=plot_params_frame)
frame.grid(row=1, column=0)
label = Label(master=frame, text="Xmax: ", font=("Arial", 12), width=label_width, anchor=W)
label.pack(side=LEFT, anchor=S)
max_x_entry = Entry(master=frame, validate="focusout", validatecommand=check, width=entry_width)
max_x_entry.pack()

frame = Frame(master=plot_params_frame)
frame.grid(row=1, column=1)
label = Label(master=frame, text="Ymax: ", font=("Arial", 12), width=label_width, anchor=W)
label.pack(side=LEFT, anchor=S)
max_y_entry = Entry(master=frame, validate="focusout", validatecommand=check, width=entry_width)
max_y_entry.pack()

frame = Frame(master=plot_params_frame)
frame.grid(row=3, column=0)
label = Label(master=frame, text="tick: ", font=("Arial", 12), width=label_width, anchor=W)
label.pack(side=LEFT, anchor=S)
tick_entry = Entry(master=frame, validate="focusout", validatecommand=check, width=entry_width)
tick_entry.pack()

show_grid_btn = Button(master=buttons_frame, text="применить", command=update_grid_params)
show_grid_btn.grid(row=2, column=0)

window.mainloop()