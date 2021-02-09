import tkinter as tk
from tkinter import ttk


class LabelCanvas(ttk.Frame):

    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        ttk.Label(self, anchor=tk.CENTER, text=title).grid(sticky=tk.NSEW)

        self.canvas = tk.Canvas(self, bg='blue')
        self.canvas.grid(sticky=tk.NSEW)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_image(self, *args, **kwargs):
        self.canvas.create_image(*args, **kwargs)


# class LabelsPanel(ttk.Frame):
#     def __init__(self, parent, *args, **kwargs):
#         self.oil_fraction = tk.StringVar()
#         self.emulsion_fraction = tk.StringVar()
#         self.water_fraction = tk.StringVar()
#
#         self.oil_fraction.set('Oil: None%')
#         self.emulsion_fraction.set('Emulsion: None%')
#         self.water_fraction.set('Water: None%')
#
#         super().__init__(parent, *args, **kwargs)
#         ttk.Label(self, textvariable=self.oil_fraction, anchor=tk.W).grid(row=0, sticky=tk.EW)
#         ttk.Label(self, textvariable=self.emulsion_fraction, anchor=tk.W).grid(row=1, sticky=tk.EW)
#         ttk.Label(self, textvariable=self.water_fraction, anchor=tk.W).grid(row=2, sticky=tk.EW)


# class TextValues(ttk.LabelFrame):
#
#     def __init__(self, parent, value_names: list, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.text_vars = {key: tk.StringVar for key in value_names}
#         for i, key in enumerate(self.text_vars.keys()):
#             ttk.Label(
#                 self,
#                 textvariable=self.text_vars[key],
#                 anchor=tk.W
#             ).grid(row=i, sticky=tk.EW)
#
#     def update_vars(self, update: dict):
#         for key, value in update.items():
#             self.text_vars[key].set(value)





class MainFrame(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


        self.image = LabelCanvas(self, 'Original')
        self.mask = LabelCanvas(self, 'Segmented')
        self.plot = LabelCanvas(self, 'Trend')


        self.image.grid(row=0, column=0, sticky=tk.NSEW)
        self.mask.grid(row=1, column=0, sticky=tk.NSEW)
        self.plot.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


class Application(tk.Tk):
    """Класс оконного приложения

    """
    background_color = '#282d2f'
    text_color = '#d4d5d5'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title('Separation Dynamics')

        self.style = ttk.Style()
        self.style.configure(
            'TFrame',
            background=Application.background_color,
            padding='0.5c'
            # borderwidth=5
        )
        self.style.configure(
            'TLabel',
            background=Application.background_color,
            foreground=Application.text_color,
            relief='flat',
            # padding='0.5c',
            font=('TkDefaultFont', 12),
        )

        MainFrame(self).grid(sticky=tk.NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)



if __name__ == '__main__':
    app = Application()
    app.mainloop()
