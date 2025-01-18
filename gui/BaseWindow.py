"""
This module provides a base class for creating Tkinter windows with common functionality.

Classes:
    - BaseWindow: A basic window setup with auto-resizing capability.
"""

DEFAULT_WINDOW_WIDTH = 1800
DEFAULT_WINDOW_HEIGHT = 900

class BaseWindow:
    """
    A base class for creating a Tkinter window with a specified title and size.

    Parameters
    ----------
    root : tk.Tk or tk.Toplevel
        The parent Tkinter root or Toplevel instance.
    title : str
        The title for the window.
    """

    def __init__(self, root, title):
        self.root = root

        # self.window = tk.Toplevel(root)
        self.window = root # For now use the root as window to fix the program not shutting down.
        self.window.title(title)
        
        width = min(DEFAULT_WINDOW_WIDTH, self.window.winfo_screenwidth() - 50)
        height = min(DEFAULT_WINDOW_HEIGHT, self.window.winfo_screenheight() - 50)
        self.window.geometry(f"{width}x{height}")
    
    def auto_resize(self):
        """
        Adjust the window size automatically based on its content.
        """
        self.window.update_idletasks()
        self.window.geometry("")
