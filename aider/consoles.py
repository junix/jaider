import json
import os
import re
import subprocess
import sys
from itertools import cycle
from typing import Literal

import rich
from colorama import init as colorama_init
from pygments.styles import get_style_by_name
from rich.box import HORIZONTALS, SQUARE
from rich.console import Console, Group

# from rich.columns import Columns
from rich.layout import Layout
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text

from aider.colors import (
    colors_jun_dark,
    generate_gradient_colors,
    get_optimal_font_color,
    morandi_colors,
    most_contrasting_color,
)

STYLE = os.getenv("DISPLAY_STYLE", "plain")


def check_env_var(var_name):
    return os.environ.get(var_name)


def get_parent_process_name():
    try:
        ppid = os.getppid()
        result = subprocess.run(
            ["ps", "-p", str(ppid), "-o", "comm="], capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception:
        return None


def detect_terminal():
    # Check for iTerm2
    if check_env_var("ITERM_SESSION_ID"):
        return "iTerm2"

    # Check for Alacritty
    if check_env_var("ALACRITTY_LOG"):
        return "Alacritty"

    # Check for Kitty
    if check_env_var("KITTY_WINDOW_ID"):
        return "Kitty"

    # Check parent process name
    parent_process = get_parent_process_name()
    if parent_process:
        if "iterm2" in parent_process.lower():
            return "iTerm2"
        elif "alacritty" in parent_process.lower():
            return "Alacritty"
        elif "kitty" in parent_process.lower():
            return "Kitty"

    # Check TERM_PROGRAM as a fallback
    term_program = check_env_var("TERM_PROGRAM")
    if term_program:
        if "iterm" in term_program.lower():
            return "iTerm2"
        elif "apple_terminal" in term_program.lower():
            return "Apple Terminal"

    return "Unknown"


def color_to_hex(color):
    """Convert rich Color object to hex code."""
    # Extract RGB triplet from the Color object
    rgb = color.triplet
    # Convert RGB to hex
    hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    return hex_color


def random_choice(seq):
    import os

    num_bytes = (len(seq) - 1).bit_length() // 8 + 1
    random_bytes = os.urandom(num_bytes)
    index = int.from_bytes(random_bytes, byteorder="big") % len(seq)
    return seq[index]


def make_style():
    if STYLE == "vivid":
        bgcolor = random_choice(colors_jun_dark)
        color = most_contrasting_color([bgcolor], morandi_colors)
        return Style(color=color, bgcolor=bgcolor)
    return Style(color="#dddddd", bgcolor="#23242e")


def yellow_bold(s):
    return f"\033[1m\033[33m{s}\033[0m"


def red_bold(s):
    return f"\033[1m\033[31m{s}\033[0m"


def green_bold(s):
    return f"\033[1m\033[32m{s}\033[0m"


def blue_bold(s):
    return f"\033[1m\033[34m{s}\033[0m"


def purple_bold(s):
    return f"\033[1m\033[35m{s}\033[0m"


def cyan_bold(s):
    return f"\033[1m\033[36m{s}\033[0m"


def white_bold(s):
    return f"\033[1m\033[37m{s}\033[0m"


def red(s):
    return f"\033[31m{s}\033[0m"


def green(s):
    return f"\033[32m{s}\033[0m"


def yellow(s):
    return f"\033[33m{s}\033[0m"


def blue(s):
    return f"\033[34m{s}\033[0m"


def purple(s):
    return f"\033[35m{s}\033[0m"


def cyan(s):
    return f"\033[36m{s}\033[0m"


def white(s):
    return f"\033[37m{s}\033[0m"


def black_bg(s):
    return f"\033[40m{s}\033[0m"


def red_bg(s):
    return f"\033[41m{s}\033[0m"


def green_bg(s):
    return f"\033[42m{s}\033[0m"


def yellow_bg(s):
    return f"\033[43m{s}\033[0m"


def blue_bg(s):
    return f"\033[44m{s}\033[0m"


def purple_bg(s):
    return f"\033[45m{s}\033[0m"


def cyan_bg(s):
    return f"\033[46m{s}\033[0m"


def white_bg(s):
    return f"\033[47m{s}\033[0m"


def reset_all_attributes(s):
    return f"\033[0m{s}\033[0m"


def bold(s):
    return f"\033[1m{s}\033[0m"


def italic(s):
    return f"\033[3m{s}\033[0m"


def underline(s):
    return f"\033[4m{s}\033[0m"


def blink(s):
    return f"\033[5m{s}\033[0m"


def reverse_view(s):
    return f"\033[7m{s}\033[0m"


def invisible(s):
    return f"\033[8m{s}\033[0m"


def strikethrough(s):
    return f"\033[9m{s}\033[0m"


_console_style_pattern = re.compile(r"^(\033\[\d+m)+")


def extract_console_color_code_from_head(s):
    """
    Extracts the console color code from the given string.

    Args:
        s (str): The input string to extract the console color code from.

    Returns:
        str or None: The console color code if found, None otherwise.
    """
    match = _console_style_pattern.match(s)
    if match:
        return match.group(0)
    return None


def print_code(
    code: str,
    *,
    title: str = None,
    language: str = "python",
    # theme: str = "catppuccin-frappe",  # "monokai",
    # theme: str = "inkpot",
    theme: str = "monokai",
    style: str = "bold green",
    console: Console = None,
    width: int = 120,  # Specify the width for wrapping
    title_align: str = "center",
    render_in_plaintext: bool = False,
) -> None:
    """
    Prints the given code with syntax highlighting, formatting, and word wrapping.

    Args:
        code (str): The code to be printed.
        language (str, optional): The language of the code. Defaults to "python".
        theme (str, optional): The theme for syntax highlighting. Defaults to "monokai".
        style (str, optional): The style for formatting. Defaults to "bold green".
        console (Console, optional): The console object to use for printing. If not provided, a new console will be created.
        title (str, optional): The title of the code block. If provided, it will be displayed in yellow bold style.
        width (int, optional): The maximum width of the code block. Defaults to 120.
        render_in_plaintext (bool, optional): If True, renders the code in plaintext without formatting. Defaults to False.

    Returns:
        None
    """
    if console is None:
        console = Console()

    if language == "json":
        if isinstance(code, (list, tuple, dict)):
            code = json.dumps(code, indent=2, ensure_ascii=False)

    if render_in_plaintext:
        console_width = console.size.width
        title = " " + (title or "Code") + " "
        print(f"{title:-^{console_width-2}}")
        print(code)
        return

    # Create a Syntax object with word wrapping
    syntax = Syntax(code, language, theme=theme, word_wrap=True)

    # Check if title is provided and adjust the title style
    if title is not None:
        title = Text(title, style="bold yellow")
        # Create a Panel object with title and width settings
        panel = Panel(
            syntax,
            title=title,
            style=style,
            border_style="dim green",
            width=width,
            title_align=title_align,
        )
    else:
        # Create a Panel object without title but with width setting
        panel = Panel(syntax, style=style, border_style="bold blue", width=width)

    console.print(place_to_center(panel, total_width=console.size.width))


def print_udf_text(
    code: str,
    *,
    title: str = None,
    style: str = "white",
    console: Console = None,
    width: int = 200,
) -> None:
    """
    Prints the given code with syntax highlighting, formatting, and word wrapping.

    Args:
        code (str): The code to be printed.
        language (str, optional): The language of the code. Defaults to "python".
        theme (str, optional): The theme for syntax highlighting. Defaults to "monokai".
        style (str, optional): The style for formatting. Defaults to "bold green".
        console (Console, optional): The console object to use for printing. If not provided, a new console will be created.
        title (str, optional): The title of the code block. If provided, it will be displayed in yellow bold style.
        width (int, optional): The maximum width of the code block. Defaults to 120.

    Returns:
        None
    """
    if console is None:
        console = Console()

    text = Text(code, style=style)
    # Check if title is provided and adjust the title style
    if title is not None:
        title = Text(title, style="bold yellow")
        # Create a Panel object with title and width settings
        panel = Panel(
            text,
            box=HORIZONTALS,
            title=title,
            style=style,
            border_style="bold blue",
            width=width,
        )
    else:
        # Create a Panel object without title but with width setting
        panel = Panel(
            text, box=HORIZONTALS, style=style, border_style="bold blue", width=width
        )

    console.print(place_to_center(panel, total_width=console.size.width))


LEFT_ARROW = "\ue0b0"
RIGHT_ARROW = "\ue0b2"

LEFT_ARROW = ""
if detect_terminal() == "iTerm2":
    RIGHT_ARROW = ""
else:
    RIGHT_ARROW = ""

bar_bg_colors = ["#601813", "#d6482f", "#f5bc82", "#155049", "#103a6e"]
bar_bg_colors = [
    "#206a82",
    "#8c89c7",
    "#18353a",
    "#476863",
    "#6f5358",
    "#0e5434",
    "#f8ac0e",
    "#9baa16",
    "#e1be56",
    "#0b6685",
    "#ff6127",
    "#3c8291",
    "#aa738e",
    "#807db1",
]


def styled_segment_text(text: str, colorset=bar_bg_colors):
    styled_text = Text()
    segments = text.split("/")
    for color, segment in zip(cycle(colorset), segments):
        styled_text.append(RIGHT_ARROW, style=color)
        font_color = get_optimal_font_color(color)
        styled_text.append(segment, style=f"{font_color} on {color}")
        styled_text.append(LEFT_ARROW, style=color)
    return styled_text


def print_markdown(
    markdown_text: str,
    *,
    style: Style = None,
    console: Console = None,
    title: str = None,
    width: int = 160,
    title_align: str = "center",
    render_in_plaintext: bool = False,
):
    if console is None:
        console = Console()

    if render_in_plaintext:
        width = console.size.width
        title = " " + title + " " if title else ""
        print(f"{title:-^{width-2}}")
        print(markdown_text)
        return

    # Fixed width
    content_width = min(width, console.size.width)

    if style is None:
        style = make_style()
    bg_color = color_to_hex(style.bgcolor)

    font_color = get_optimal_font_color(bg_color)
    if font_color == "black":
        code_theme = "bw"
    else:
        code_theme = "bw"

    # https://pygments.org/styles/
    markdown = Markdown(
        markdown_text,
        code_theme="catppuccin-macchiato",
        # code_theme="one-dark",
        # inline_code_lexer="python",
        inline_code_theme="catppuccin-latte",
    )
    if title:
        colorset = generate_gradient_colors(bg_color)
        colorset = [colorset[0], colorset[2]]
        styled_title = styled_segment_text(title, colorset=colorset)
    else:
        styled_title = None

    panel = Panel(
        markdown,
        title=styled_title,
        box=SQUARE,
        padding=(1, 2),
        border_style="black" if STYLE == "vivid" else "dim cyan",
        width=content_width,
        title_align=title_align,
        # style=Style(color="white", bgcolor="black"),
        style=style,
        # expand=True,
    )

    console.print(place_to_center(panel, total_width=console.size.width))


def place_to_center(layout, *, total_width):
    if layout.width > total_width:
        return layout

    left_padding = (total_width - layout.width) // 2
    left_padding = max(left_padding, 0)  # Ensure left_padding is not negative

    # Apply padding to center the panel
    return Padding(layout, (0, 0, 0, left_padding))


colors = [
    "bold yellow",
    "bold magenta",
    "bold blue",
    "bold red",
    "bold cyan",
    "bold green",
]


def print_compare_markdown(
    *contents,
    format: str = "markdown",
):
    """
    Prints two pieces of markdown text side by side for comparison.

    Args:
        left (str): The markdown text to display on the left.
        right (str): The markdown text to display on the right.
    """
    console = Console()

    # Create the left markdown panel
    layouts = []
    for index, (content, title) in enumerate(contents):
        text_len = len(content)
        if format == "markdown":
            content = Markdown(content)
        else:
            content = Syntax(content, format, word_wrap=True)

        color = colors[index]
        panel = Panel(
            content,
            title=Text(title, style=color),
            border_style=color,
            style=make_style(),
            expand=True,
        )
        layouts.append(Layout(panel, ratio=text_len))

    # Create a layout and add the panels side by side
    layout = Layout()
    layout.split_row(*layouts)
    console.print(layout)

    # group = Group(*panels)
    # console.print(group)

    # 使用 Columns 创建左右排列的布局
    # layout = Columns(panels, expand=True, equal=False, right_to_left=True)
    # console.print(layout)


# Print the layout


def print_pair(*, src: str, dst: str, src_title: str, dst_title: str) -> None:
    """
    Prints a pair of source and destination strings in a formatted console output.

    Args:
        src (str): The source string to be displayed.
        dst (str): The destination string to be displayed.
        src_title (str): The title for the source panel.
        dst_title (str): The title for the destination panel.

    Returns:
        None
    """
    console = rich.console.Console()
    # Create the title for the source panel
    src_title = Text(src_title, style="bold green underline")
    src_panel = Panel(src, title=src_title, style="on blue")

    # Create the title for the destination panel
    dst_title = Text(dst_title, style="bold yellow underline")
    dst_panel = Panel(dst, title=dst_title, style="on red")

    # Create a group of panels
    panel_group = Group(src_panel, dst_panel)
    # Print the group of panels
    console.print(place_to_center(panel_group, total_width=console.size.width))


def is_atty():
    import io

    return sys.stdout.isatty() and not isinstance(sys.stdout, io.TextIOWrapper)


def set_cursor_shape(shape: Literal["block", "underline", "bar"]):
    if shape == "block":
        shape = 0
    elif shape == "underline":
        shape = 1
    elif shape == "bar":
        shape = 2
    else:
        raise ValueError(f"Invalid cursor shape: {shape}")

    sys.stdout.write(f"\033]50;CursorShape={shape}\007")
    sys.stdout.flush()


def set_window_title(title):
    """
    OSC 2: 设置窗口标题
    """
    sys.stdout.write(f"\033]2;{title}\007")
    sys.stdout.flush()


def set_hyperlink(uri: str, text: str = None):
    """
    OSC 8: 创建超链接
    """
    if not text:
        text = uri
    sys.stdout.write(f"\033]8;;{uri}\033\\{text}\033]8;;\033\\")
    sys.stdout.flush()


def set_clipboard(text, selection="c"):
    """
    OSC 52: 设置剪贴板内容
    selection: 'c' 为系统剪贴板, 'p' 为主选择
    """
    import base64

    encoded = base64.b64encode(text.encode()).decode()
    sys.stdout.write(f"\033]52;{selection};{encoded}\007")
    sys.stdout.flush()


from enum import Enum


class ClearMode(Enum):
    CURSOR_TO_END = 0
    START_TO_CURSOR = 1
    ENTIRE = 2


def clear_screen(mode: ClearMode = ClearMode.ENTIRE):
    """
    清除屏幕的部分或全部区域
    mode:
        ClearMode.CURSOR_TO_END (0) - 从光标位置清除到屏幕末尾
        ClearMode.START_TO_CURSOR (1) - 从屏幕开头清除到光标位置
        ClearMode.ENTIRE (2) - 清除整个屏幕
    """
    sys.stdout.write(f"\033[{mode.value}J")
    sys.stdout.flush()


def clear_line(mode: ClearMode = ClearMode.ENTIRE):
    """
    清除当前行的部分或全部区域
    mode:
        ClearMode.CURSOR_TO_END (0) - 从光标位置清除到行尾
        ClearMode.START_TO_CURSOR (1) - 从行首清除到光标位置
        ClearMode.ENTIRE (2) - 清除整行
    """
    sys.stdout.write(f"\033[{mode.value}K")
    sys.stdout.flush()


def save_cursor_position():
    """
    保存当前光标位置
    """
    sys.stdout.write("\033[s")
    sys.stdout.flush()


def restore_cursor_position():
    """
    恢复之前保存的光标位置
    """
    sys.stdout.write("\033[u")
    sys.stdout.flush()
