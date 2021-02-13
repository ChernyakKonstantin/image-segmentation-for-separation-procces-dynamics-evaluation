import tkinter as tk
from tkinter import ttk


class LabelCanvas(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.canvas = tk.Canvas(self, bg='blue')
        self.canvas.grid(sticky=tk.NSEW)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_image(self, *args, **kwargs):
        self.canvas.create_image(*args, **kwargs)

    def grid(self, sticky=tk.NSEW, **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def get_canvas_size(self):
        return int(self.canvas['width']), int(self.canvas['height'])


class LabelText(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.text = tk.Text(self, yscrollcommand=self.scrollbar.set)

        self.scrollbar.config(command=self.text.yview)

        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        self.scrollbar.grid(row=0, column=1, sticky=tk.NSEW)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

    def grid(self, sticky=tk.NSEW, **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def write_new_line(self, text):
        self.text.insert(tk.END, text + '\n')


class MainFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.image = LabelCanvas(
            self,
            text='Original',
            labelanchor=tk.N,
        )
        self.mask = LabelCanvas(
            self,
            text='Segmented',
            labelanchor=tk.N,
        )
        self.plot = LabelCanvas(
            self,
            text='Plot',
            labelanchor=tk.N,
        )
        self.info = LabelText(
            self,
            text='Info',
            labelanchor=tk.NW,
        )
        self.image.place(x=0, y=0, height=310, width=420)
        self.mask.place(x=0, y=310, height=310, width=420)
        self.plot.place(x=420, y=0, height=620, width=860)
        self.info.place(x=0, y=620, height=100, width=1280)
