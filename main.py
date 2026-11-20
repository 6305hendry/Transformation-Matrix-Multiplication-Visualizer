import math
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Made with Github Copilot

class RotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transformation matrix")
        self.root.geometry("1100x760")

        main = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main, width=350)
        right = ttk.Frame(main)
        main.add(left, weight=0)
        main.add(right, weight=1)

        self.left_canvas = tk.Canvas(left, highlightthickness=0, width=330)
        left_scrollbar = ttk.Scrollbar(
            left, orient=tk.VERTICAL, command=self.left_canvas.yview
        )
        self.left_canvas.configure(yscrollcommand=left_scrollbar.set)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        controls = ttk.Frame(self.left_canvas, padding=12)
        self.left_canvas_window = self.left_canvas.create_window(
            (0, 0), window=controls, anchor="nw"
        )
        controls.bind("<Configure>", self._update_scroll_region)
        self.left_canvas.bind("<Configure>", self._resize_controls)
        self.root.bind_all("<MouseWheel>", self._scroll_left_panel)

        self.frame_values = {"new_frame": {}, "transformation": {}}
        self.matrix_texts = {}
        self.input_status = ttk.Label(controls, text="", foreground="firebrick")

        ttk.Button(controls, text="Reset View", command=self.reset_view).pack(
            fill=tk.X, pady=(0, 4)
        )
        ttk.Button(controls, text="Reset position", command=self.reset_position).pack(
            fill=tk.X, pady=4
        )
        self.grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls,
            text="Show grid",
            variable=self.grid_var,
            command=self.update_plot,
        ).pack(anchor="w", pady=4)

        self.plot_t1_t2_var = tk.BooleanVar(value=True)
        self.plot_t2_t1_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            controls,
            text="Plot T1*T2",
            variable=self.plot_t1_t2_var,
            command=self.update_plot,
        ).pack(anchor="w", pady=2)
        ttk.Checkbutton(
            controls,
            text="Plot T2*T1",
            variable=self.plot_t2_t1_var,
            command=self.update_plot,
        ).pack(anchor="w", pady=2)

        ttk.Separator(controls, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Label(
            controls, text="T1", font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))
        self._add_transform_controls(controls, "new_frame")
        self._add_matrix_display(controls, "T1 matrix", "new_frame")

        ttk.Separator(controls, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Label(controls, text="T2", font=("TkDefaultFont", 10, "bold")).pack(
            anchor="w", pady=(0, 4)
        )
        self._add_transform_controls(controls, "transformation")
        self._add_matrix_display(controls, "T2 matrix", "transformation")

        ttk.Separator(controls, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._add_matrix_display(controls, "T1*T2 matrix", "result_t1_t2")
        self._add_matrix_display(controls, "T2*T1 matrix", "result_t2_t1")
        self.input_status.pack(anchor="w", pady=(6, 0))

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111, projection="3d")
        self.ax.view_init(elev=25, azim=35, roll=0)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, right)
        self.toolbar.update()

        self.update_plot()

    def _update_scroll_region(self, _event=None):
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))

    def _resize_controls(self, event):
        self.left_canvas.itemconfigure(self.left_canvas_window, width=event.width)

    def _scroll_left_panel(self, event):
        pointer_x = self.root.winfo_pointerx()
        canvas_left = self.left_canvas.winfo_rootx()
        if canvas_left <= pointer_x <= canvas_left + self.left_canvas.winfo_width():
            self.left_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _add_transform_controls(self, parent, transform_name):
        ttk.Label(parent, text="Position (X, Y, Z)").pack(anchor="w", pady=(3, 0))
        self._add_spinboxes(parent, transform_name, ("X", "Y", "Z"), 0.1)
        ttk.Label(parent, text="Orientation (Roll, Pitch, Yaw)").pack(
            anchor="w", pady=(4, 0)
        )
        self._add_spinboxes(parent, transform_name, ("Roll", "Pitch", "Yaw"), 1)

    def _add_spinboxes(self, parent, transform_name, names, increment):
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        for name in names:
            cell = ttk.Frame(row)
            cell.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
            ttk.Label(cell, text=name, anchor="w").pack(anchor="w")
            value = tk.StringVar(value="0")
            self.frame_values[transform_name][name] = value
            spinbox = ttk.Spinbox(
                cell,
                from_=-1_000_000,
                to=1_000_000,
                increment=increment,
                textvariable=value,
                width=9,
            )
            spinbox.pack(fill=tk.X)
            value.trace_add("write", self.update_plot)

    def _add_matrix_display(self, parent, title, matrix_name):
        ttk.Label(parent, text=title).pack(anchor="w", pady=(4, 1))
        text = tk.Text(parent, height=4, width=44, font=("Consolas", 8), wrap=tk.NONE)
        text.pack(fill=tk.X)
        text.configure(state=tk.DISABLED)
        self.matrix_texts[matrix_name] = text

    def _read_transform_values(self, transform_name):
        values = {
            name: float(value.get())
            for name, value in self.frame_values[transform_name].items()
        }
        if not all(math.isfinite(value) for value in values.values()):
            raise ValueError("Transform values must be finite.")
        return values

    def _set_matrix_text(self, matrix_name, rows):
        text = "\n".join(
            "[ " + "  ".join(f"{value: .4f}" for value in row) + " ]"
            for row in rows
        )
        widget = self.matrix_texts[matrix_name]
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.configure(state=tk.DISABLED)

    def _rotation_matrix(self, roll, pitch, yaw):
        roll, pitch, yaw = map(math.radians, (roll, pitch, yaw))
        cr, sr = math.cos(roll), math.sin(roll)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cy, sy = math.cos(yaw), math.sin(yaw)
        return (
            (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
            (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
            (-sp, cp * sr, cp * cr),
        )

    def _make_transform(self, values):
        x, y, z = (values[name] for name in ("X", "Y", "Z"))
        rotation = self._rotation_matrix(
            values["Roll"], values["Pitch"], values["Yaw"]
        )
        matrix = (
            (*rotation[0], x),
            (*rotation[1], y),
            (*rotation[2], z),
            (0.0, 0.0, 0.0, 1.0),
        )
        return matrix, rotation, (x, y, z)

    def _multiply_transforms(self, left, right):
        return tuple(
            tuple(
                sum(left[row][index] * right[index][column] for index in range(4))
                for column in range(4)
            )
            for row in range(4)
        )

    def _draw_reference_axes(self, limit):
        axis_colors = ("darkred", "darkgreen", "darkblue")
        for index, (color, label) in enumerate(zip(axis_colors, ("X", "Y", "Z"))):
            endpoint = [0.0, 0.0, 0.0]
            endpoint[index] = 1.0
            self.ax.quiver(
                0, 0, 0, *endpoint, color=color, linewidth=1.8, arrow_length_ratio=0.15
            )
            self.ax.text(*endpoint, label, color=color, fontweight="bold")

        self.ax.plot([-limit, limit], [0, 0], [0, 0], color="black", linewidth=0.7)
        self.ax.plot([0, 0], [-limit, limit], [0, 0], color="black", linewidth=0.7)
        self.ax.plot([0, 0], [0, 0], [-limit, limit], color="black", linewidth=0.7)

    def _draw_frame(self, origin, rotation, linestyle, linewidth, label_suffix):
        colors = ("red", "limegreen", "blue")
        for index, color in enumerate(colors):
            endpoint = tuple(
                origin[row] + rotation[row][index] for row in range(3)
            )
            self.ax.plot(
                [origin[0], endpoint[0]],
                [origin[1], endpoint[1]],
                [origin[2], endpoint[2]],
                color=color,
                linewidth=linewidth,
                linestyle=linestyle,
            )
            if label_suffix is not None:
                self.ax.text(
                    *endpoint,
                    f"{'xyz'[index]}{label_suffix}",
                    color=color,
                    fontweight="bold",
                )

    def _draw_translation_projection(self, origin):
        x, y, z = origin
        self.ax.plot([0, x], [0, 0], [0, 0], color="gray", linewidth=0.45, linestyle=":")
        self.ax.plot([x, x], [0, y], [0, 0], color="gray", linewidth=0.45, linestyle=":")
        self.ax.plot([x, x], [y, y], [0, z], color="gray", linewidth=0.45, linestyle=":")

    def _apply_grid_visibility(self):
        show_grid = self.grid_var.get()
        self.ax.grid(show_grid)
        for axis in (self.ax.xaxis, self.ax.yaxis, self.ax.zaxis):
            axis.pane.fill = show_grid
            axis.pane.set_facecolor((1, 1, 1, 1 if show_grid else 0))
        if not show_grid:
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_zticks([])

    def reset_position(self):
        for values in self.frame_values.values():
            for name in ("X", "Y", "Z"):
                values[name].set("0")
            for name in ("Roll", "Pitch", "Yaw"):
                values[name].set("0")
        self.update_plot()

    def reset_view(self):
        self.ax.view_init(elev=25, azim=35, roll=0)
        self.canvas.draw_idle()

    def update_plot(self, *_):
        elevation, azimuth = self.ax.elev, self.ax.azim
        self.ax.clear()
        self.ax.view_init(elev=elevation, azim=azimuth, roll=0)

        try:
            first_values = self._read_transform_values("new_frame")
            second_values = self._read_transform_values("transformation")
        except ValueError:
            self.input_status.configure(text="Enter finite numbers in every field.")
            for matrix_name in self.matrix_texts:
                self._set_matrix_text(matrix_name, [])
            first_matrix = second_matrix = None
            first_rotation = second_rotation = None
            first_origin = (0.0, 0.0, 0.0)
            result_t1_t2_matrix = result_t2_t1_matrix = None
            result_t1_t2_rotation = result_t2_t1_rotation = None
            result_t1_t2_origin = result_t2_t1_origin = (0.0, 0.0, 0.0)
        else:
            self.input_status.configure(text="")
            first_matrix, first_rotation, first_origin = self._make_transform(first_values)
            second_matrix, second_rotation, _ = self._make_transform(second_values)

            result_t1_t2_matrix = self._multiply_transforms(first_matrix, second_matrix)
            result_t2_t1_matrix = self._multiply_transforms(second_matrix, first_matrix)
            result_t1_t2_rotation = tuple(
                tuple(result_t1_t2_matrix[row][column] for column in range(3))
                for row in range(3)
            )
            result_t2_t1_rotation = tuple(
                tuple(result_t2_t1_matrix[row][column] for column in range(3))
                for row in range(3)
            )
            result_t1_t2_origin = tuple(result_t1_t2_matrix[row][3] for row in range(3))
            result_t2_t1_origin = tuple(result_t2_t1_matrix[row][3] for row in range(3))
            self._set_matrix_text("new_frame", first_matrix)
            self._set_matrix_text("transformation", second_matrix)
            self._set_matrix_text("result_t1_t2", result_t1_t2_matrix)
            self._set_matrix_text("result_t2_t1", result_t2_t1_matrix)

        visible_origins = [first_origin]
        if self.plot_t1_t2_var.get():
            visible_origins.append(result_t1_t2_origin)
        if self.plot_t2_t1_var.get():
            visible_origins.append(result_t2_t1_origin)
        extent = max(
            2.5,
            *(abs(value) + 1.3 for origin in visible_origins for value in origin),
        )
        self._draw_reference_axes(extent)
        if first_matrix is not None:
            self._draw_frame(first_origin, first_rotation, ":", 2.0, "1")
            if self.plot_t1_t2_var.get():
                self._draw_translation_projection(result_t1_t2_origin)
                self._draw_frame(
                    result_t1_t2_origin, result_t1_t2_rotation, "-", 2.5, "12"
                )
            if self.plot_t2_t1_var.get():
                self._draw_translation_projection(result_t2_t1_origin)
                self._draw_frame(
                    result_t2_t1_origin, result_t2_t1_rotation, "--", 2.5, "21"
                )

        self.ax.set_xlim(-extent, extent)
        self.ax.set_ylim(-extent, extent)
        self.ax.set_zlim(-extent, extent)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_box_aspect((1, 1, 1))
        self._apply_grid_visibility()
        self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = RotationApp(root)
    root.mainloop()
