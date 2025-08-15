import logging
import os
import select
import sys

from colour import Color

from exponent.utils.colors import (
    adjust_color_for_contrast,
    blend_colors_srgb,
    color_distance,
)

logger = logging.getLogger(__name__)


DEFAULT_TERM_PALETTE = [
    # Windows 10 Console default palette.
    # The least bad default of them all ;)
    # Used as a fallback when terminal doesn't report its palette,
    # which only happens on older or feature-poor terminals, i.e. very rarely.
    Color("#0c0c0c"),
    Color("#c50f1f"),
    Color("#13a10e"),
    Color("#c19c00"),
    Color("#0037da"),
    Color("#881798"),
    Color("#3a96dd"),
    Color("#cccccc"),
]


# As the only popular "modern" terminal emulator, Terminal.app doesn't support true color
# so disable true color output if we're running in it.
TRUE_COLOR = os.getenv("TERM_PROGRAM") != "Apple_Terminal"


class Theme:
    term_fg: Color
    term_bg: Color
    red: Color
    green: Color
    blue: Color
    exponent_green: Color
    hl_theme_name: str
    dimmed_text_fg: Color
    block_header_bg: Color
    block_body_bg: Color
    block_footer_fg: Color
    block_footer_bg: Color
    statusbar_default_fg: Color
    statusbar_autorun_all: Color
    statusbar_autorun_ro: Color
    statusbar_thinking_on: Color
    thinking_spinner_fg: Color

    def __init__(
        self, term_fg: Color, term_bg: Color, term_palette: list[Color | None]
    ):
        self.term_fg = term_bg
        self.term_bg = term_bg
        self.red = adjust_color_for_contrast(
            term_bg, term_palette[1] or DEFAULT_TERM_PALETTE[1]
        )
        self.green = adjust_color_for_contrast(
            term_bg, term_palette[2] or DEFAULT_TERM_PALETTE[2]
        )
        self.blue = adjust_color_for_contrast(
            term_bg, term_palette[4] or DEFAULT_TERM_PALETTE[4]
        )
        self.exponent_green = adjust_color_for_contrast(
            term_bg,
            Color("#03bd89"),  # green used in Exponent logo
        )
        dark_mode = term_bg.luminance < 0.5
        self.hl_theme_name = "ansi_dark" if dark_mode else "ansi_light"
        direction = 1 if dark_mode else -1
        (h, s, l) = term_bg.hsl  # noqa: E741
        block_target = Color(hsl=(h, s, min(1.0, l + 0.005 * direction)))
        self.block_header_bg = adjust_color_for_contrast(term_bg, block_target, 1.2)
        self.block_body_bg = adjust_color_for_contrast(term_bg, block_target, 1.1)
        self.block_footer_bg = adjust_color_for_contrast(term_bg, block_target, 1.05)
        self.block_footer_fg = blend_colors_srgb(term_fg, self.block_footer_bg, 0.4)
        self.dimmed_text_fg = adjust_color_for_contrast(
            term_bg, blend_colors_srgb(term_fg, term_bg, 0.5)
        )
        self.statusbar_default_fg = self.dimmed_text_fg
        self.statusbar_autorun_all = self.red
        self.statusbar_autorun_ro = self.green
        self.statusbar_thinking_on = self.blue
        self.thinking_spinner_fg = adjust_color_for_contrast(
            term_bg, Color("#968ce6")
        )  # nice purple


def get_term_colors(
    use_default_colors: bool,
) -> tuple[Color, Color, list[Color | None]]:
    from exponent.commands.shell_commands import POSIX_TERMINAL, RawMode

    fg = DEFAULT_TERM_PALETTE[7]
    bg = DEFAULT_TERM_PALETTE[0]
    palette: list[Color | None] = [None, None, None, None, None, None, None, None]

    # Not supported on Windows or when stdin is not a TTY
    if use_default_colors or not POSIX_TERMINAL or not sys.stdin.isatty():
        return (fg, bg, palette)

    try:
        with RawMode(sys.stdin.fileno()):
            stdin_fd = sys.stdin.fileno()
            stdout_fd = sys.stdout.fileno()

            # Try to write the ANSI escape sequences
            if stdout_fd in select.select([], [stdout_fd], [], 1)[1]:
                os.write(
                    stdout_fd,
                    b"\x1b]10;?\x07\x1b]11;?\x07\x1b]4;0;?\x07\x1b]4;1;?\x07\x1b]4;2;?\x07\x1b]4;3;?\x07\x1b]4;4;?\x07\x1b]4;5;?\x07\x1b]4;6;?\x07\x1b]4;7;?\x07\x1b[c",
                )
            else:
                return (fg, bg, palette)  # Can't write to stdout

            got_da_response = False
            timeout = 0.5  # Short timeout to avoid hanging

            # Read terminal responses until we get DA response or timeout
            while not got_da_response:
                if stdin_fd in select.select([stdin_fd], [], [], timeout)[0]:
                    reply = os.read(stdin_fd, 1024)
                    seqs = reply.split(b"\x1b")

                    for seq in seqs:
                        if seq.startswith(b"]10;rgb:"):
                            [r, g, b] = seq[8:].decode().split("/")
                            fg = Color(f"#{r[0:2]}{g[0:2]}{b[0:2]}")
                        elif seq.startswith(b"]11;rgb:"):
                            [r, g, b] = seq[8:].decode().split("/")
                            bg = Color(f"#{r[0:2]}{g[0:2]}{b[0:2]}")
                        elif seq.startswith(b"]4;"):
                            text = seq.decode()
                            idx = int(text[3])
                            [r, g, b] = text[9:].split("/")
                            palette[idx] = Color(f"#{r[0:2]}{g[0:2]}{b[0:2]}")
                        elif seq.endswith(b"c"):
                            got_da_response = True
                else:
                    # Timeout, terminal didn't respond
                    break
    except Exception:
        logger.debug("Error getting term colors", exc_info=True)
        # Any exception at all, just use default colors
        pass

    return (fg, bg, palette)


def color_component_to_8bit_cube(value: int) -> tuple[int, int]:
    # Based on https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit

    if value < 48:
        value = 0
        idx = 0
    elif value < 115:
        value = 0x5F
        idx = 1
    elif value < 155:
        value = 0x87
        idx = 2
    elif value < 195:
        value = 0xAF
        idx = 3
    elif value < 235:
        value = 0xD7
        idx = 4
    else:
        value = 0xFF
        idx = 5

    return (value, idx)


def closest_8bit_color_index(c: Color) -> int:
    (quantized_red, red_idx) = color_component_to_8bit_cube(round(c.red * 255))
    (quantized_green, green_idx) = color_component_to_8bit_cube(round(c.green * 255))
    (quantized_blue, blue_idx) = color_component_to_8bit_cube(round(c.blue * 255))
    quantized = Color(
        rgb=(quantized_red / 255, quantized_green / 255, quantized_blue / 255)
    )
    quantized_error = color_distance(c, quantized)

    gray = Color(hsl=(c.hue, 0, c.luminance))
    gray_idx = round(max(gray.red * 255 - 8, 0) / 10)
    quantized_gray_value = 8 + 10 * gray_idx
    quantized_gray = Color(
        rgb=(
            quantized_gray_value / 255,
            quantized_gray_value / 255,
            quantized_gray_value / 255,
        )
    )
    quantized_gray_error = color_distance(c, quantized_gray)

    if quantized_error < quantized_gray_error:
        # 16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
        idx = 16 + 36 * red_idx + 6 * green_idx + blue_idx
    else:
        idx = 232 + gray_idx

    return idx


def fg_color_seq(c: int | Color) -> str:
    if isinstance(c, int):
        return f"\x1b[{30 + c}m"
    elif TRUE_COLOR:
        (r, g, b) = c.rgb
        r = round(r * 255)
        g = round(g * 255)
        b = round(b * 255)
        return f"\x1b[38;2;{r};{g};{b}m"
    else:
        idx = closest_8bit_color_index(c)
        return f"\x1b[38;5;{idx}m"


def default_fg_color_seq() -> str:
    return "\x1b[39m"


def bg_color_seq(c: int | Color) -> str:
    if isinstance(c, int):
        return f"\x1b[{40 + c}m"
    elif TRUE_COLOR:
        (r, g, b) = c.rgb
        r = round(r * 255)
        g = round(g * 255)
        b = round(b * 255)
        return f"\x1b[48;2;{r};{g};{b}m"
    else:
        idx = closest_8bit_color_index(c)
        return f"\x1b[48;5;{idx}m"


def get_theme(use_default_colors: bool) -> Theme:
    (fg, bg, palette) = get_term_colors(use_default_colors)
    return Theme(fg, bg, palette)
