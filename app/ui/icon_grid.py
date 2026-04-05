# сетка иконок

import customtkinter as ctk
from tkinter import Menu
from pathlib import Path
from PIL import Image
from ..models import Shortcut
from ..windows_utils import launch_app, show_properties, extract_icon

class IconGrid:
    def __init__(self, parent, on_delete_callback):
        self.parent = parent
        self.on_delete = on_delete_callback
        self.buttons = []

    def clear(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.buttons.clear()

    def add_icon(self, app: Shortcut):
        frame = ctk.CTkFrame(self.parent, fg_color="transparent", width=130, height=150)
        frame.grid_propagate(False)

        icon_path = extract_icon(app.lnk_path, app.name)
        if icon_path and Path(icon_path).exists():
            img = Image.open(icon_path).resize((64, 64))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64))
        else:
            ctk_img = None

        btn = ctk.CTkButton(
            frame,
            text="",
            image=ctk_img,
            width=90,
            height=90,
            fg_color="#2D2D2D",
            hover_color="#404040",
            command=lambda: launch_app(app.lnk_path)
        )
        btn.pack(pady=(10, 5))

        label = ctk.CTkLabel(frame, text=app.name[:18] + ("..." if len(app.name) > 18 else ""),
                             font=ctk.CTkFont(size=12))
        label.pack()

        # Правый клик
        def right_click(event):
            menu = Menu(self.parent, tearoff=0, bg="#2D2D2D", fg="white")
            menu.add_command(label="Удалить", command=lambda: self.on_delete(app))
            menu.tk_popup(event.x_root, event.y_root)

        btn.bind("<Button-3>", right_click)
        frame.bind("<Button-3>", right_click)

        self.buttons.append(frame)
        return frame