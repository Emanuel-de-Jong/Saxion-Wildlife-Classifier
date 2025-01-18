import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Accordion(tk.Frame):
    def __init__(self, parent, title="Item", is_expanded=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.title = title
        self.is_expanded = is_expanded

        # Create button to toggle the frame
        self.toggle_button = tk.Button(self, text=self.title, command=self.toggle)
        self.toggle_button.pack(fill="x")

        # Create the collapsible frame
        self.body = tk.Frame(self)
        self._expand()

        if not self.is_expanded:
            self._collapse()

        # Track the current position for adding new plots
        self.row = 0
        self.col = 0

    def add_to_body(self, fig):
        # Create the plot canvas
        plot_canvas = FigureCanvasTkAgg(fig, self.body)
        plot_canvas.draw()

        # Get the tkinter widget from the canvas
        widget = plot_canvas.get_tk_widget()
        widget.grid(row=self.row, column=self.col)

        # Update row and column for next widget
        self.col += 1
        if self.col >= 2:
            self.col = 0
            self.row += 1

    def toggle(self):
        if self.is_expanded:
            self._collapse()
        else:
            self._expand()

        self.is_expanded = not self.is_expanded

    def _expand(self):
        self.body.pack(fill="x", expand=True)

    def _collapse(self):
        self.body.pack_forget()
