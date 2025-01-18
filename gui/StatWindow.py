"""
This module implements the StatWindow class, a specialized GUI window for displaying various statistics.

Classes:
    - StatWindow: Extends BaseWindow to provide functionality for displaying plots and charts.
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from BaseWindow import BaseWindow
from GUIData import GUIData
from Accordion import Accordion

STATS_FIG_SIZE = (16, 8)

class StatWindow(BaseWindow):
    """
    A specialized window for displaying statistical data using charts and plots.

    Parameters
    ----------
    root : tk.Tk or tk.Toplevel
        The parent Tkinter root or Toplevel instance.
    title : str
        The window title.
    gui_tunnel : queue.Queue
        The queue for receiving data updates.
    """
    def __init__(self, root, title, gui_tunnel):
        super().__init__(root, title)

        self.gui_tunnel = gui_tunnel

        # Configure the root window to expand the container
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Create a container frame
        self.container = ttk.Frame(self.window)
        self.container.grid(row=0, column=0, sticky="nsew")

        # Create a main canvas with scrollbars
        self.canvas = tk.Canvas(self.container)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.v_scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure scrolling behavior
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Layout for canvas and scrollbars
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)

        # Add Accordion
        self.accordions = {}
        self._add_accordion("results", "Results", True)
        self._add_accordion("stats", "Statistics")

        self._check_for_data()
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(-1 * (event.delta // 120), "units")
    
    def _add_accordion(self, name, title, is_expanded=False):
        accordion = Accordion(self.scrollable_frame, title, is_expanded)
        accordion.pack(fill="x", pady=5)
        self.accordions[name] = accordion

    def _check_for_data(self):
        """
        Periodically checks for data in the queue and updates the GUI.
        """
        while not self.gui_tunnel.empty():
            tunnel_package = self.gui_tunnel.get()

            if isinstance(tunnel_package, GUIData):
                data = tunnel_package.data

                if tunnel_package.name == "title":
                    self.window.title(data)
                elif tunnel_package.name == "annotation_examples":
                    for labeled_image in data:
                        self._show_annotation_example(labeled_image)
                elif tunnel_package.name == "stats":
                    self._show_observations_by_specie(data)
                    self._show_observations_by_camera(data)
                    self._show_observations_by_leging(data)
                    for specie in data['species_by_hour'].keys():
                        self._show_specie_by_hour(data, specie)
            else:
                print(f"Received data in GUI: {tunnel_package}")

        self.window.after(100, self._check_for_data)

    def _show_annotation_example(self, labeled_image):
        fig = Figure(figsize=(6, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.imshow(labeled_image["image"])

        for annotation in labeled_image["annotations"]:
            x_min, y_min, x_max, y_max = annotation["bbox"]
            width = x_max - x_min
            height = y_max - y_min
            rect = Rectangle((x_min, y_min), width, height, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

            text = f"{annotation['category']}: {annotation['score']:.2f}"
            ax.text(
                x_min + 4,
                y_min - 20,
                text,
                color='white',
                fontsize=10,
                bbox=dict(facecolor='red', alpha=0.5, edgecolor='red', boxstyle='round,pad=0.2'),
            )

        ax.axis("off")

        self.accordions["results"].add_to_body(fig)

    def _show_observations_by_specie(self, data):
        observations_by_specie = data['observations_by_specie']
        if len(observations_by_specie) == 0:
            print("There is no data available to plot.")
            return

        species = list(observations_by_specie.keys())
        observations = list(observations_by_specie.values())

        fig = Figure(figsize=STATS_FIG_SIZE)
        ax = fig.add_subplot(111)
        ax.bar(species, observations, color='skyblue')
        ax.set_title('Observations by Specie')
        ax.set_ylabel('Number of Observations')
        ax.set_xticks(range(len(species)))
        ax.set_xticklabels(species, rotation=45)
        
        self.accordions["stats"].add_to_body(fig)

    def _show_observations_by_camera(self, data):
        observations_by_camera = data['observations_by_camera']
        if len(observations_by_camera) == 0:
            print("There is no data available to plot.")
            return

        cameras = list(observations_by_camera.keys())
        observations = list(observations_by_camera.values())

        fig = Figure(figsize=STATS_FIG_SIZE)
        ax = fig.add_subplot(111)
        ax.bar(cameras, observations, color='skyblue')
        ax.set_title('Observations by Camera')
        ax.set_ylabel('Number of Observations')
        ax.set_xticks(range(len(cameras)))
        ax.set_xticklabels(cameras, rotation=45)
        
        self.accordions["stats"].add_to_body(fig)

    def _show_observations_by_leging(self, data):
        observations_by_leging = data['observations_by_leging']
        if len(observations_by_leging) == 0:
            print("There is no data available to plot.")
            return

        legings = list(observations_by_leging.keys())
        observations = list(observations_by_leging.values())

        fig = Figure(figsize=STATS_FIG_SIZE)
        ax = fig.add_subplot(111)
        ax.bar(legings, observations, color='skyblue')
        ax.set_title('Observations by Leging')
        ax.set_ylabel('Number of Observations')
        ax.set_xticks(range(len(legings)))
        ax.set_xticklabels(legings, rotation=45)
        
        self.accordions["stats"].add_to_body(fig)

    def _show_specie_by_hour(self, data, specie):
        specie_by_hour = data['species_by_hour'][specie]
        if len(specie_by_hour) == 0:
            print("There is no data available to plot.")
            return
        
        hours = range(24)
        observations = [0] * 24
        for i in range(24):
            if str(i) in specie_by_hour:
                observations[i] = specie_by_hour[str(i)]

        fig = Figure(figsize=STATS_FIG_SIZE)
        ax = fig.add_subplot(111)
        ax.plot(hours, observations, marker='o')
        ax.set_title(f"Observations of {specie} by Hour")
        ax.set_xlabel("Hour of the Day")
        ax.set_ylabel("Number of Observations")
        ax.set_xticks(hours)
        ax.grid(True)

        if not specie in self.accordions:
            self._add_accordion(specie, specie.title())
        
        self.accordions[specie].add_to_body(fig)
