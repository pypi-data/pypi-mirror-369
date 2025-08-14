import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from CTkColorPicker import AskColor, CTkColorPicker


def open_modal_picker():
    picker = AskColor(initial_color=modal_swatch.cget("fg_color"))
    color = picker.get()
    if color:
        modal_swatch.configure(fg_color=color)


def update_embedded_picker(color: str):
    embedded_swatch.configure(fg_color=color)


if __name__ == "__main__":
    ctk.set_appearance_mode("system")              # "light", "dark", or "system"
    # ctk.set_default_color_theme("dark-blue")     # optional accent theme

    root = ctk.CTk()
    root.title("CTkColorPicker Demo")

    # Modal color picker demo
    modal_frame = ctk.CTkFrame(root)
    modal_frame.pack(padx=20, pady=10, fill="x")

    modal_swatch = ctk.CTkFrame(modal_frame, width=30, height=30, fg_color="#ffffff")
    modal_swatch.pack(side="left")
    modal_swatch.pack_propagate(False)

    modal_button = ctk.CTkButton(
        modal_frame, text="Open Modal Picker", command=open_modal_picker
    )
    modal_button.pack(side="left", padx=10)

    # Embedded color picker demo
    embedded_frame = ctk.CTkFrame(root)
    embedded_frame.pack(padx=20, pady=10, fill="both", expand=True)

    embedded_swatch = ctk.CTkFrame(
        embedded_frame, width=30, height=30, fg_color="#ffffff"
    )
    embedded_picker = CTkColorPicker(
        embedded_frame,
        width=250,
        command=update_embedded_picker,
        initial_color=embedded_swatch.cget("fg_color"),
    )
    embedded_picker.pack(side="left")

    embedded_swatch.pack(side="left", padx=10)
    embedded_swatch.pack_propagate(False)

    root.mainloop()
