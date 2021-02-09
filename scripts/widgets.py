import tkinter as tk
from tkinter import ttk


class LabelCanvas(ttk.Frame):

    def __init__(self, parent, title, canvas_width, canvas_height, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = ttk.Label(self, anchor=tk.CENTER, text=title)
        self.canvas = tk.Canvas(self, bg='blue', width=canvas_width, height=canvas_height)

        self.title.grid(row=0, sticky=tk.EW)
        self.canvas.grid(row=1, sticky=tk.NSEW)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def grid(self, sticky=tk.NSEW, **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def create_image(self, *args, **kwargs):
        self.canvas.create_image(*args, **kwargs)


class LabelsPanel(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.oil_fraction = tk.StringVar()
        self.emulsion_fraction = tk.StringVar()
        self.water_fraction = tk.StringVar()

        self.oil_fraction.set('Oil: None%')
        self.emulsion_fraction.set('Emulsion: None%')
        self.water_fraction.set('Water: None%')

        super().__init__(parent, *args, **kwargs)
        ttk.Label(self, textvariable=self.oil_fraction, anchor=tk.W).grid(row=0, sticky=tk.EW)
        ttk.Label(self, textvariable=self.emulsion_fraction, anchor=tk.W).grid(row=1, sticky=tk.EW)
        ttk.Label(self, textvariable=self.water_fraction, anchor=tk.W).grid(row=2, sticky=tk.EW)


class MainFrame(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


        self.image = LabelCanvas(self, 'Original', canvas_width=400, canvas_height=300)
        self.mask = LabelCanvas(self, 'Segmented', canvas_width=400, canvas_height=300)
        self.plot = LabelCanvas(self, 'Trend', canvas_width=800, canvas_height=600)

        self.status_info = ttk.Entry(self)

        self.image.grid(row=0, column=0)
        self.mask.grid(row=1, column=0)
        self.plot.grid(row=0, column=1, rowspan=2)

        self.status_info.grid(row=2, column=0, columnspan=2)


class Application(tk.Tk):
    """Класс оконного приложения

    """
    background_color = '#282d2f'
    text_color = '#d4d5d5'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title('Separation Dynamics')

        style = ttk.Style()
        style.configure(
            'TFrame',
            background=Application.background_color,
            # borderwidth=5
        )
        style.configure(
            'TLabel',
            background=Application.background_color,
            foreground=Application.text_color,
            relief='flat',
            font=('TkDefaultFont', 12),
        )

        MainFrame(self).grid()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


if __name__ == '__main__':
    app = Application()
    app.mainloop()
