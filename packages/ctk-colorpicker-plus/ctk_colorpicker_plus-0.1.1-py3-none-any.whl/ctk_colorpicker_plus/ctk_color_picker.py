# CTk Color Picker for customtkinter
# Original Author: Akash Bora (Akascape)
# Contributers: Victor Vimbert-Guerlais (helloHackYnow)

import tkinter
import customtkinter
from PIL import Image, ImageTk
import os
import math
import colorsys
from typing import Any
from .color_utils import (
    projection_on_circle,
    update_colors as utils_update_colors,
    normalize_hex,
    build_hue_to_angle_lookup,
    hue_to_angle,
    TAU,
)

PATH = os.path.dirname(os.path.realpath(__file__))


class AskColor(customtkinter.CTkToplevel):
    """Toplevel dialog for selecting a color via a wheel and slider."""

    def __init__(
        self,
        width: int = 300,
        title: str = "Choose Color",
        initial_color: str | None = None,
        bg_color: str | None = None,
        fg_color: str | None = None,
        button_color: str | None = None,
        button_hover_color: str | None = None,
        text: str = "OK",
        corner_radius: int = 24,
        slider_border: int = 1,
        **button_kwargs: Any,
    ) -> None:
        """Initialize the color picker dialog.

        Parameters
        ----------
        width : int
            Width of the dialog window in pixels. Minimum accepted value is
            200.
        title : str
            Title of the dialog window.
        initial_color : str | None
            Starting color in hexadecimal format.
        bg_color : str | None
            Background color for the dialog.
        fg_color : str | None
            Foreground color of the inner frame.
        button_color : str | None
            Fill color of the confirmation button.
        button_hover_color : str | None
            Hover color of the confirmation button.
        text : str
            Text displayed on the confirmation button.
        corner_radius : int
            Corner radius applied to widgets.
        slider_border : int
            Border width for the brightness slider.
        **button_kwargs : Any
            Additional keyword arguments forwarded to the confirmation
            button.
        """

        super().__init__()

        self.title(title)
        WIDTH = width if width >= 200 else 200
        HEIGHT = WIDTH + 150
        self.image_dimension = self._apply_window_scaling(WIDTH - 100)
        self.target_dimension = self._apply_window_scaling(20)

        self.maxsize(WIDTH, HEIGHT)
        self.minsize(WIDTH, HEIGHT)
        self.resizable(width=False, height=False)
        self.transient(self.master)
        self.lift()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.after(10)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.default_hex_color = "#ffffff"
        self.default_rgb = [255, 255, 255]
        self.rgb_color = self.default_rgb[:]

        self.bg_color = (
            self._apply_appearance_mode(
                customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
            )
            if bg_color is None
            else bg_color
        )
        self.fg_color = (
            self._apply_appearance_mode(
                customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"]
            )
            if fg_color is None
            else fg_color
        )
        self.button_color = (
            self._apply_appearance_mode(
                customtkinter.ThemeManager.theme["CTkButton"]["fg_color"]
            )
            if button_color is None
            else button_color
        )
        self.button_hover_color = (
            self._apply_appearance_mode(
                customtkinter.ThemeManager.theme["CTkButton"]["hover_color"]
            )
            if button_hover_color is None
            else button_hover_color
        )
        self.button_text = text
        self.corner_radius = corner_radius
        self.slider_border = 10 if slider_border >= 10 else slider_border

        self.config(bg=self.bg_color)

        self.frame = customtkinter.CTkFrame(
            master=self, fg_color=self.fg_color, bg_color=self.bg_color
        )
        self.frame.grid(padx=20, pady=20, sticky="nswe")

        self.canvas = tkinter.Canvas(
            self.frame,
            height=self.image_dimension,
            width=self.image_dimension,
            highlightthickness=0,
            bg=self.fg_color,
        )
        self.canvas.pack(pady=20)
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
            master=self.frame,
            height=20,
            border_width=self.slider_border,
            button_length=15,
            progress_color=self.default_hex_color,
            from_=0,
            to=255,
            variable=self.brightness_slider_value,
            number_of_steps=256,
            button_corner_radius=self.corner_radius,
            corner_radius=self.corner_radius,
            button_color=self.button_color,
            button_hover_color=self.button_hover_color,
            command=lambda x: self.update_colors(),
        )
        self.slider.pack(fill="both", pady=(0, 15), padx=20 - self.slider_border)

        self.entry = customtkinter.CTkEntry(
            master=self.frame,
            text_color="#000000",
            height=50,
            fg_color=self.default_hex_color,
            corner_radius=self.corner_radius,
            justify="center",
        )
        self.entry.insert(0, self.default_hex_color)
        self.entry.bind("<FocusOut>", self.apply_hex_input)
        self.entry.bind("<Return>", self.apply_hex_input)
        self.entry.pack(fill="both", padx=10)

        self.set_initial_color(initial_color)

        self.button = customtkinter.CTkButton(
            master=self.frame,
            text=self.button_text,
            height=50,
            corner_radius=self.corner_radius,
            fg_color=self.button_color,
            hover_color=self.button_hover_color,
            command=self._ok_event,
            **button_kwargs,
        )
        self.button.pack(fill="both", padx=10, pady=20)

        self.after(150, lambda: self.entry.focus())

        self.grab_set()

    def get(self) -> str | None:
        """Return the color selected by the user.

        The method blocks until the dialog window is closed and then returns
        the currently selected color.

        Returns
        -------
        str | None
            Hexadecimal color string or ``None`` if the dialog was closed
            without selection.
        """

        self._color = self.default_hex_color
        self.master.wait_window(self)
        return self._color

    def _ok_event(self, event: tkinter.Event | None = None) -> None:
        """Confirm the selection and close the dialog.

        Parameters
        ----------
        event : tkinter.Event | None
            Optional event object from button or keyboard interaction.
        """

        self.apply_hex_input()
        self._color = self.default_hex_color
        self.grab_release()
        self.destroy()
        del self.img1
        del self.img2
        del self.wheel
        del self.target

    def _on_closing(self) -> None:
        """Handle the window close event by discarding the selection."""

        self._color = None
        self.grab_release()
        self.destroy()
        del self.img1
        del self.img2
        del self.wheel
        del self.target

    def on_mouse_drag(self, event: tkinter.Event) -> None:
        """Move the target when the user clicks or drags the mouse.

        Parameters
        ----------
        event : tkinter.Event
            Event containing the mouse coordinates.
        """

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
        """Update widget colors based on the current selection and brightness."""

        brightness = self.brightness_slider_value.get()
        self.rgb_color, self.default_hex_color = utils_update_colors(
            self.img1,
            getattr(self, "target_x", 0),
            getattr(self, "target_y", 0),
            brightness,
            self.slider,
            self.entry,
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

    def set_initial_color(self, initial_color: str | None) -> None:
        """Position the target and widgets according to ``initial_color``.

        Parameters
        ----------
        initial_color : str | None
            Hexadecimal color string used to initialize the target position.
        """

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
            return

        self.target_x = self.image_dimension / 2
        self.target_y = self.image_dimension / 2
        self.canvas.delete("all")
        self.canvas.create_image(
            self.image_dimension / 2, self.image_dimension / 2, image=self.wheel
        )
        self.canvas.create_image(self.target_x, self.target_y, image=self.target)
