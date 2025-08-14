# ctk-colorpicker-plus
An extended and modernized color picker for [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), featuring both a modal dialog and embeddable widget with a color wheel, brightness slider, and hex entry.

Forked from the original **CTkColorPicker** by [Akash Bora (Akascape)](https://github.com/Akascape) — with bug fixes, enhancements, and new features.

![Modal color picker, light and dark](https://github.com/user-attachments/assets/7811857c-4367-4b2d-9ced-e3ad02f03f68)

---

## Features

- **Two usage modes**:
  - `AskColor` — modal dialog for picking a color
  - `CTkColorPicker` — embeddable widget for your layouts
- **Accurate reticle positioning** — fixed hue/saturation calculation bug
- **Brightness slider** — smooth 0–255 range
- **Hex entry field** — accepts user input, short (`#fff`) or full (`#ffffff`) hex values
- **Real-time updates** — changes propagate immediately to the UI and optional callbacks
- **Appearance-mode aware** — adapts to light/dark or system themes in CustomTkinter
- Fully type-hinted and `ruff`/`black` formatted

[![Animated Demo](https://github.com/user-attachments/assets/84337580-acef-4481-bc6a-3d4990da149b)](https://www.youtube.com/watch?v=WLTVBCdxEOA)

---

## Installation

From PyPI (once published):

```
pip install ctk-colorpicker-plus
```
Until then, install from GitHub:
```
pip install git+https://github.com/calusasoft/ctk-colorpicker-plus.git
```

---

## Quick Start

### Modal Dialog
![Modal color picker dialog, light-themed](https://github.com/user-attachments/assets/6e6b9948-859e-4d53-8053-497881a8e5da)
```
import customtkinter
from ctk_colorpicker_plus import AskColor

customtkinter.set_appearance_mode("light")

root = customtkinter.CTk()

def pick_color():
    dialog = AskColor(initial_color="#ff0000")
    color = dialog.get()
    if color:
        print(f"Selected: {color}")

btn = customtkinter.CTkButton(root, text="Pick a color", command=pick_color)
btn.pack(pady=20)

root.mainloop()
```

### Embedded Widget
![Embedded color picker widget, dark-themed](https://github.com/user-attachments/assets/ef1e87bb-9ba5-445a-aa94-54f4861abc06)
```
import customtkinter
from ctk_colorpicker_plus import CTkColorPicker

def on_color_change(hex_color: str):
    print(f"Color changed: {hex_color}")

root = customtkinter.CTk()
picker = CTkColorPicker(root, command=on_color_change)
picker.pack(padx=20, pady=20)

root.mainloop()
```

---

## Project Structure
```
ctk_colorpicker_plus/
    __init__.py
    ctk_color_picker.py          # Modal dialog
    ctk_color_picker_widget.py   # Embeddable widget
    color_utils.py               # Shared color math and helpers
    color_wheel.png
    target.png
examples/
    demo.py
```

---

## Requirements
- Python 3.8+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow](https://pypi.org/project/pillow/)

Install dependencies:
```
pip install customtkinter Pillow
```

---

## License
This project is released under the MIT License.
> **Attribution:** Based on _CTkColorPicker_ by Akash Bora (Akasacape), originally released under CC0.

---

## Credits
- **Original Author:** Akash Bora (Akascape) — [GitHub](https://github.com/Akascape)
- **Maintainer:** Phil Rice - [GitHub](https://github.com/calusasoft)
- **Contributors:** Victor Vimbert-Guerlais and the open source community
