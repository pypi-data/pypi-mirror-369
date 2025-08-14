import math
import colorsys
from typing import Callable
from PIL import Image
import string
import bisect

TAU = 2 * math.pi
"""Full circle constant ``2π`` used for angle calculations."""

HUE_OFFSET = 0
"""Legacy hue offset (no longer applied)."""


def normalize_hex(value: str | None) -> str | None:
    """Return a normalized ``#rrggbb`` color string or ``None`` if invalid."""

    if value is None:
        return None
    value = value.strip().lower()
    if not value:
        return None
    if value.startswith("#"):
        value = value[1:]
    if len(value) == 3 and all(c in string.hexdigits for c in value):
        return "#" + "".join(c * 2 for c in value)
    if len(value) == 6 and all(c in string.hexdigits for c in value):
        return "#" + value
    return None


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Return the HSV representation of an RGB color."""

    return colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """Return the integer RGB representation of an HSV color."""

    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def projection_on_circle(
    point_x: float, point_y: float, circle_x: float, circle_y: float, radius: float
) -> tuple[float, float]:
    """Project a point onto the circumference of a circle."""
    angle = math.atan2(point_y - circle_y, point_x - circle_x)
    projection_x = circle_x + radius * math.cos(angle)
    projection_y = circle_y + radius * math.sin(angle)
    return projection_x, projection_y


def update_colors(
    image: Image.Image,
    target_x: int,
    target_y: int,
    brightness: int,
    slider: any,
    widget: any,
    command: Callable[[str], None] | None = None,
    get_callback: Callable[[], str] | None = None,
    angle_lookup: tuple[list[float], list[float]] | None = None,
) -> tuple[list[int], str]:
    """Update color widgets and return the RGB list and hex color.

    The color is derived from ``target_x``/``target_y`` relative to the wheel
    center. Hue and saturation are computed geometrically and combined with the
    provided ``brightness`` value to form the final RGB color using
    :func:`colorsys.hsv_to_rgb`.
    """

    w, h = image.size
    cx, cy = w / 2, h / 2
    dx = target_x - cx
    dy = cy - target_y  # invert y-axis for cartesian coordinates

    angle = math.atan2(dy, dx) % TAU
    if angle_lookup is not None:
        h_val = angle_to_hue(angle, angle_lookup)
    else:
        h_val = (angle % TAU) / TAU

    radius = math.sqrt(dx * dx + dy * dy)
    max_radius = min(cx, cy) - 1
    s_val = min(radius / max_radius, 1.0)
    v_val = brightness / 255

    r_f, g_f, b_f = colorsys.hsv_to_rgb(h_val, s_val, v_val)
    rgb_color = [int(round(r_f * 255)), int(round(g_f * 255)), int(round(b_f * 255))]
    hex_color = "#{:02x}{:02x}{:02x}".format(*rgb_color)

    slider.configure(progress_color=hex_color)

    if hasattr(widget, "delete"):
        widget.configure(fg_color=hex_color)
        widget.delete(0, "end")
        widget.insert(0, hex_color)
    else:
        try:
            widget.configure(fg_color=hex_color, text=str(hex_color))
        except Exception:
            widget.configure(fg_color=hex_color)

    if brightness < 70:
        widget.configure(text_color="white")
    else:
        widget.configure(text_color="black")
    if str(widget._fg_color) == "black":
        widget.configure(text_color="white")

    if command and get_callback:
        command(get_callback())

    return rgb_color, hex_color


def build_hue_to_angle_lookup(
    image: Image.Image, samples: int = 1024, ring: float = 0.985
) -> tuple[list[float], list[float]]:
    """
    Build a hue→angle lookup from the *resized* wheel.

    - Samples a ring near the outer hue band (ring≈0.985).
    - Unwraps hue across the 1→0 discontinuity so the sequence is strictly increasing.
    - Rotates and normalizes back to 0..1 for clean interpolation.
    """
    w, h = image.size
    cx, cy = w / 2, h / 2
    R = min(cx, cy) - 1
    r_sample = R * ring

    raw_hues: list[float] = []
    angles: list[float] = []

    for i in range(samples):
        t = (i / samples) * TAU  # angle 0..2π
        x = int(round(cx + r_sample * math.cos(t)))
        y = int(round(cy - r_sample * math.sin(t)))
        r, g, b = image.getpixel((x, y))[:3]
        h_, s_, v_ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        raw_hues.append(h_)
        angles.append(t)

    # Unwrap circular hue: whenever we cross 1→0, add +1.0
    unwrapped: list[float] = []
    offset = 0.0
    prev = None
    for h_ in raw_hues:
        val = h_ + offset
        if prev is not None:
            # strong decrease → we crossed the wrap; move to next turn
            if val < prev - 0.5:
                offset += 1.0
                val = h_ + offset
            # tiny noise decreases → clamp to monotonic
            if val < prev:
                val = prev
        unwrapped.append(val)
        prev = val

    # Rotate and normalize to 0..1
    start = unwrapped[0]
    span = unwrapped[-1] - start
    if span <= 0:
        # extremely pathological; fall back to identity
        hues_norm = [0.0 + (i / (samples - 1)) for i in range(samples)]
    else:
        hues_norm = [(v - start) / span for v in unwrapped]

    return hues_norm, angles


def hue_to_angle(h: float, lookup: tuple[list[float], list[float]]) -> float:
    """Interpolate wheel angle (0..TAU) for HSV hue h (0..1) using the lookup."""
    hues, angles = lookup
    i = bisect.bisect_left(hues, h)
    if i <= 0:
        return angles[0]
    if i >= len(hues):
        return angles[-1]
    h0, h1 = hues[i - 1], hues[i]
    t0, t1 = angles[i - 1], angles[i]
    if h1 == h0:
        return t0
    # linear interpolation
    return t0 + (t1 - t0) * ((h - h0) / (h1 - h0))


def angle_to_hue(angle: float, lookup: tuple[list[float], list[float]]) -> float:
    """Interpolate HSV hue (0..1) for wheel angle a (0..TAU) using the lookup."""
    hues, angles = lookup
    a = angle % TAU
    i = bisect.bisect_left(angles, a)
    if i <= 0:
        return hues[0]
    if i >= len(angles):
        return hues[-1]
    a0, a1 = angles[i - 1], angles[i]
    h0, h1 = hues[i - 1], hues[i]
    if a1 == a0:
        return h0
    return h0 + (h1 - h0) * ((a - a0) / (a1 - a0))
