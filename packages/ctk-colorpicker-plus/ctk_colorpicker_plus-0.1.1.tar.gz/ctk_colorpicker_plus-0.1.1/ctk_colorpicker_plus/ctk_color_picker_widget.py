# CTk Color Picker widget for customtkinter
# Author: Akash Bora (Akascape)

import tkinter
import customtkinter
from PIL import Image, ImageTk
import os
import math
import colorsys
from typing import Any, Callable

from .color_utils import (
    projection_on_circle,
    update_colors as utils_update_colors,
    normalize_hex,
    build_hue_to_angle_lookup,
    hue_to_angle,
    TAU,
)

PATH = os.path.dirname(os.path.realpath(__file__))


class CTkColorPicker(customtkinter.CTkFrame):
    """A color picker widget with a color wheel and brightness slider."""

    def __init__(
        self,
        master: Any | None = None,
        width: int = 300,
        initial_color: str | None = None,
        fg_color: str | None = None,
        slider_border: int = 1,
        corner_radius: int = 24,
        command: Callable[[str], None] | None = None,
        orientation: str = "vertical",
        **slider_kwargs: Any,
    ) -> None:
        """Create a color picker widget.

        Parameters
        ----------
        master : Any | None
            Parent widget.
        width : int
            Width of the color wheel in pixels. Minimum accepted value is
            200.
        initial_color : str | None
            Starting color in hexadecimal format.
        fg_color : str | None
            Foreground color of the frame.
        slider_border : int
            Border width for the brightness slider.
        corner_radius : int
            Corner radius applied to internal widgets.
        command : Callable[[str], None] | None
            Callback invoked with the selected color whenever it changes.
        orientation : str
            Orientation of the slider, either ``"vertical"`` or
            ``"horizontal"``.
        **slider_kwargs : Any
            Additional keyword arguments passed to the slider.
        """

        super().__init__(master=master, corner_radius=corner_radius)

        WIDTH = width if width >= 200 else 200
        self.image_dimension = int(self._apply_widget_scaling(WIDTH - 100))
        self.target_dimension = int(self._apply_widget_scaling(20))
        self.lift()

        self.after(10)
        self.default_hex_color = "#ffffff"
        self.default_rgb = [255, 255, 255]
        self.rgb_color = self.default_rgb[:]

        self.fg_color = (
            self._apply_appearance_mode(self._fg_color)
            if fg_color is None
            else fg_color
        )
        self.corner_radius = corner_radius

        self.command = command

        self.slider_border = 10 if slider_border >= 10 else slider_border

        self.configure(fg_color=self.fg_color)
        self.wheel_frame = customtkinter.CTkFrame(self, fg_color="transparent")

        self.canvas = tkinter.Canvas(
            self.wheel_frame,
            height=self.image_dimension,
            width=self.image_dimension,
            highlightthickness=0,
            bg=self.fg_color,
        )
        self.canvas.bind("<Button-1>", self.on_mouse_drag)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

        with Image.open(os.path.join(PATH, "color_wheel.png")) as img:
            self.img1 = img.resize(
                (self.image_dimension, self.image_dimension),
                Image.Resampling.LANCZOS,
            )
            self.wheel = ImageTk.PhotoImage(self.img1)

        # Build hue angle map
        self._hue_lookup = build_hue_to_angle_lookup(self.img1)

        with Image.open(os.path.join(PATH, "target.png")) as img:
            self.img2 = img.resize(
                (self.target_dimension, self.target_dimension),
                Image.Resampling.LANCZOS,
            )
            self.target = ImageTk.PhotoImage(self.img2)

        self.canvas.create_image(
            self.image_dimension / 2, self.image_dimension / 2, image=self.wheel
        )
        self.brightness_slider_value = customtkinter.IntVar()
        self.brightness_slider_value.set(255)

        self.slider = customtkinter.CTkSlider(
            master=self.wheel_frame,
            width=20,
            border_width=self.slider_border,
            button_length=15,
            progress_color=self.default_hex_color,
            from_=0,
            to=255,
            variable=self.brightness_slider_value,
            number_of_steps=256,
            button_corner_radius=self.corner_radius,
            corner_radius=self.corner_radius,
            command=lambda x: self.update_colors(),
            orientation=orientation,
            **slider_kwargs,
        )

        self.entry = customtkinter.CTkEntry(
            master=self,
            text_color="#000000",
            width=10,
            fg_color=self.default_hex_color,
            corner_radius=self.corner_radius,
            justify="center",
        )
        self.entry.insert(0, self.default_hex_color)
        self.entry.bind("<FocusOut>", self.apply_hex_input)
        self.entry.bind("<Return>", self.apply_hex_input)

        if orientation == "vertical":
            self.canvas.pack(pady=20, side="left", padx=(10, 0))
            self.slider.pack(
                fill="y", pady=15, side="right", padx=(10, 10 - self.slider_border)
            )
            self.wheel_frame.pack(side="top")
            self.entry.pack(fill="x", padx=10, pady=(0, 15))
        else:
            try:
                self.entry.configure(wraplength=100)
            except (tkinter.TclError, ValueError):
                pass
            self.canvas.pack(pady=(0, 15))
            self.slider.pack(fill="x", pady=(0, 10 - self.slider_border))
            self.wheel_frame.pack(pady=15, padx=15)
            self.entry.pack(expand=True, fill="both", padx=15, pady=(0, 15))

        self.set_initial_color(initial_color)

    def get(self) -> str:
        """Return the currently selected color as a hexadecimal string."""

        self._color = self.entry._fg_color
        return self._color

    def destroy(self) -> None:
        """Destroy the widget and free associated image resources."""

        super().destroy()
        del self.img1
        del self.img2
        del self.wheel
        del self.target

    def on_mouse_drag(self, event: tkinter.Event) -> None:
        """Move the target when the user clicks or drags on the wheel."""

        x = event.x
        y = event.y
        self.canvas.delete("all")
        self.canvas.create_image(
            self.image_dimension / 2, self.image_dimension / 2, image=self.wheel
        )

        d_from_center = math.sqrt(
            ((self.image_dimension / 2) - x) ** 2
            + ((self.image_dimension / 2) - y) ** 2
        )

        if d_from_center < self.image_dimension / 2:
            self.target_x, self.target_y = x, y
        else:
            self.target_x, self.target_y = projection_on_circle(
                x,
                y,
                self.image_dimension / 2,
                self.image_dimension / 2,
                self.image_dimension / 2 - 1,
            )

        self.canvas.create_image(self.target_x, self.target_y, image=self.target)

        self.update_colors()

    def update_colors(self) -> None:
        """Update widget colors and invoke the callback if provided."""

        brightness = self.brightness_slider_value.get()
        self.rgb_color, self.default_hex_color = utils_update_colors(
            self.img1,
            getattr(self, "target_x", 0),
            getattr(self, "target_y", 0),
            brightness,
            self.slider,
            self.entry,
            command=self.command,
            get_callback=self.get,
            angle_lookup=self._hue_lookup,
        )

    def apply_hex_input(self, event: tkinter.Event | None = None) -> None:
        """Validate and apply the hex color entered by the user."""

        value = self.entry.get().strip()
        normalized = normalize_hex(value)
        if normalized is None:
            self.entry.delete(0, "end")
            self.entry.insert(0, self.default_hex_color)
            self.entry.configure(fg_color=self.default_hex_color)
            self.slider.configure(progress_color=self.default_hex_color)
            self.brightness_slider_value.set(255)
            self.entry.focus()
            return

        r, g, b = tuple(int(normalized[i : i + 2], 16) for i in (1, 3, 5))
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        value = int(v * 255)
        self.brightness_slider_value.set(value)

        try:
            angle = hue_to_angle(h, self._hue_lookup)
        except Exception:
            angle = (h * TAU) % TAU  # safety fallback

        radius = s * (self.image_dimension / 2 - 1)
        self.target_x = self.image_dimension / 2 + radius * math.cos(angle)
        self.target_y = self.image_dimension / 2 - radius * math.sin(angle)

        self.canvas.delete("all")
        self.canvas.create_image(
            self.image_dimension / 2, self.image_dimension / 2, image=self.wheel
        )
        self.canvas.create_image(self.target_x, self.target_y, image=self.target)

        self.default_hex_color = normalized
        rgb = [r, g, b]
        self.rgb_color = rgb[:]
        self.default_rgb = rgb[:]
        self.entry.delete(0, "end")
        self.entry.insert(0, normalized)
        self.entry.configure(fg_color=normalized)
        self.slider.configure(progress_color=normalized)

        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        if brightness < 70 or normalized == "#000000":
            self.entry.configure(text_color="white")
        else:
            self.entry.configure(text_color="black")

        if self.command:
            self.command(self.get())

    def set_initial_color(self, initial_color: str | None) -> None:
        """Position the target and widgets to match ``initial_color``."""

        normalized = normalize_hex(initial_color) if initial_color else None
        if normalized is not None:
            r, g, b = tuple(int(normalized[i : i + 2], 16) for i in (1, 3, 5))
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

            value = int(v * 255)
            self.brightness_slider_value.set(value)

            try:
                angle = hue_to_angle(h, self._hue_lookup)
            except Exception:
                angle = (h * TAU) % TAU  # safety fallback

            radius = s * (self.image_dimension / 2 - 1)
            self.target_x = self.image_dimension / 2 + radius * math.cos(angle)
            self.target_y = self.image_dimension / 2 - radius * math.sin(angle)

            self.canvas.delete("all")
            self.canvas.create_image(
                self.image_dimension / 2, self.image_dimension / 2, image=self.wheel
            )
            self.canvas.create_image(self.target_x, self.target_y, image=self.target)

            self.default_hex_color = normalized
            rgb = [r, g, b]
            self.rgb_color = rgb[:]
            self.default_rgb = rgb[:]

            self.entry.delete(0, "end")
            self.entry.insert(0, normalized)
            self.entry.configure(fg_color=normalized)
            self.slider.configure(progress_color=normalized)

            brightness = 0.299 * r + 0.587 * g + 0.114 * b
            if brightness < 70 or normalized == "#000000":
                self.entry.configure(text_color="white")
            else:
                self.entry.configure(text_color="black")

            if self.command:
                self.command(self.get())
            return

        self.target_x = self.image_dimension / 2
        self.target_y = self.image_dimension / 2
        self.canvas.delete("all")
        self.canvas.create_image(
            self.image_dimension / 2, self.image_dimension / 2, image=self.wheel
        )
        self.canvas.create_image(self.target_x, self.target_y, image=self.target)
