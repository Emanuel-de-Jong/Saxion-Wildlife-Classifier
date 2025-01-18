"""
This module defines a simple data container class for passing data to the GUI.

Classes:
    - GUIData: Encapsulates name and data for use in GUI elements.
"""

class GUIData:
    """
    Encapsulates a name and associated data.

    Parameters
    ----------
    name : str
        The name identifier for the data.
    data : Any
        The associated data.
    """
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def print(self):
        """
        Prints the data in a formatted string.
        """
        print(f"Name: {self.name}, Data: {self.data}")
