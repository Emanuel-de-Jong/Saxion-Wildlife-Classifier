import tkinter as tk
import queue
from StatWindow import StatWindow
from GUIData import GUIData

gui_tunnel = queue.Queue()
root = None

def init():
    global gui_tunnel
    global root

    root = tk.Tk()
    # For now don't withdraw as the StatWindow uses the root as temp fix.
    # root.withdraw()

    # Create the main StatWindow
    stat_window = StatWindow(root, "Statistics", gui_tunnel)

def put(name, data):
    """
    Puts data into the GUI tunnel.

    Parameters
    ----------
    name : str
        The name of the data item.
    data : Any
        The data to send to the GUI.
    """
    global gui_tunnel
    gui_tunnel.put(GUIData(name, data))

def mainloop():
    global root
    if root:
        root.mainloop()
