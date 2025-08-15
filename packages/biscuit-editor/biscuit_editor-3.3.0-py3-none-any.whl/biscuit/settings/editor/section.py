import tkinter as tk

from biscuit.common.ui import Frame

from .items import CheckboxItem, DropdownItem, IntegerItem, StringItem


class Section(Frame):
    """Section for the settings editor to group the items together.

    - Add items to the section to change the settings
    - Add a title to the section to describe the settings
    """

    def __init__(self, master, title="", *args, **kwargs) -> None:
        """Initialize the section with a title

        Args:
            master (tk.Tk): root window
            title (str, optional): title of the section. Defaults to"""

        super().__init__(master, *args, **kwargs)
        self.config(**self.base.theme.editors, padx=30)

        self.items = []
        tk.Label(
            self,
            text=title,
            font=("Segoi UI", 22, "bold"),
            anchor=tk.W,
            **self.base.theme.editors.labels
        ).pack(fill=tk.X, expand=True)

    def add_dropdown(
        self, name="Example", options=["True", "False"], default=0
    ) -> None:
        """Add a dropdown item to the section

        Args:
            name (str, optional): name of the dropdown. Defaults to "Example".
            options (list, optional): list of options for the dropdown. Defaults to ["True", "False"].
            default (int, optional): default value of the dropdown. Defaults to 0.
        """

        dropdown = DropdownItem(self, name, options, default)
        dropdown.pack(fill=tk.X, expand=True)
        self.items.append(dropdown)

    def add_stringvalue(self, name="Example", default="placeholder") -> None:
        """Add a string text box item to the section

        Args:
            name (str, optional): name of the string. Defaults to "Example".
            default (str, optional): default value of the string. Defaults to "placeholder".
        """

        string = StringItem(self, name, default)
        string.pack(fill=tk.X, expand=True)
        self.items.append(string)

    def add_intvalue(self, name="Example", default="0") -> None:
        """Add an integer text box item to the section

        Args:
            name (str, optional): name of the integer. Defaults to "Example".
            default (int, optional): default value of the integer. Defaults to "0".
        """

        int = IntegerItem(self, name, default)
        int.pack(fill=tk.X, expand=True)
        self.items.append(int)

    def add_checkbox(self, name="Example", default=True) -> None:
        """Add a checkbox item to the section

        Args:
            name (str, optional): name of the checkbox. Defaults to "Example".
            default (bool, optional): default value of the checkbox. Defaults to True.
        """

        dropdown = CheckboxItem(self, name, default)
        dropdown.pack(fill=tk.X, expand=True)
        self.items.append(dropdown)
