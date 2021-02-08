import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2 as cv
import numpy as np
from threading import Thread


class LabelCanvas(ttk.Frame):

    def __init__(self, parent, title, canvas_size, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.title = ttk.Label(self, anchor=tk.CENTER, text=title)
        self.canvas = tk.Canvas(
            self,
            bg='blue',
            highlightbackground=BACKGROUND_COLOR,
            height=canvas_size[1],
            width=canvas_size[0]
        )

        # self.title.grid(row=0, column=0, sticky=tk.EW)
        self.canvas.grid(row=1, column=0, sticky=tk.NSEW)

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
        self.image = LabelCanvas(self, 'Original', (400, 300))
        self.mask = LabelCanvas(self, 'Segmented', (400, 300))
        self.plot = LabelCanvas(self, 'Trend', (800, 600))
        # self.data = LabelsPanel(self)



        # img = Image.open("image.jpg")
        # img = img.resize((100, 100))
        # self.img = ImageTk.PhotoImage(img)
        self.img = gen_img()
        self.image.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.image.grid(row=0, column=0)
        self.mask.grid(row=1, column=0)
        self.plot.grid(row=0, column=1, rowspan=2)
        # self.data.grid(row=0, column=3)


    def grid(self, sticky=tk.NSEW, **kwargs):
        super().grid(sticky=sticky, **kwargs)


def gen_img():
    """I made it just to test."""
    img = np.random.randint(low=0, high=255, size=(300, 300, 3), dtype='uint8')
    return ImageTk.PhotoImage(Image.fromarray(img))

BACKGROUND_COLOR = '#282d2f'
TEXT_COLOR = '#d4d5d5'


root = tk.Tk()
root.title('Separation Dynamics')
# root.attributes("-fullscreen", True)
style = ttk.Style()
style.configure(
    'TFrame',
    background=BACKGROUND_COLOR,
    relief='flat',
    borderwidth=5
)
style.configure(
    'TLabel',
    background=BACKGROUND_COLOR,
    foreground=TEXT_COLOR,
    relief='flat',
    font=('TkDefaultFont', 12),
)

# root.geometry('1280x720')
# root.resizable(False, False)

MainFrame(root).grid(row=0, column=0)
root.mainloop()