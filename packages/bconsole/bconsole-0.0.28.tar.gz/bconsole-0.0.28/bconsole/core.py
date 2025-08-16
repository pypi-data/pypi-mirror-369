from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from re import findall as find_all
from sys import stdin, stdout
from typing import Any, Final, Literal, NoReturn, TextIO, final, override

from .utils import CombinableMetaclass, hex_to_rgb, hsl_to_rgb

__all__ = [
    "TerminalColor",
    "Foreground",
    "Background",
    "Modifier",
    "Cursor",
    "Erase",
]

_ESC = "\033"


class _ImmutableMeta(CombinableMetaclass):
    """
    Metaclass that makes classes immutable, not their instances.
    Does not prevent the addition of new attributes.
    """

    @final
    def __setattr__(cls, name: str, value: Any) -> None:
        if name in cls.__dict__:
            raise AttributeError(f"Cannot reassign constant {name!r}")
        super().__setattr__(name, value)

    @final
    def __delattr__(cls, name: str) -> NoReturn:
        raise AttributeError(f"Cannot delete attribute {name!r}")


class _Uninitiliazable:
    """Makes classes uninitializable. Kinda like static classes in other languages!"""

    @final
    def __new__(cls) -> NoReturn:
        raise RuntimeError(f"Class {cls.__name__} is uninitializable!")

    @final
    def __init__(self) -> None: ...


class TerminalColor(_Uninitiliazable, ABC, metaclass=_ImmutableMeta and ABCMeta):
    """Abstract class for terminal colors."""

    RESET: Final = f"{_ESC}[0m"

    @staticmethod
    @abstractmethod
    def from_rgb(r: int, g: int, b: int, /) -> str:
        """
        Creates a True Color Escape Code Sequence for the terminal color using the RGB values provided.\n
        Note that this functionality is not supported by all terminals.

        ### Args:
            r (int): red channel
            g (int): green channel
            b (int): blue channel

        ### Returns:
            str: Escape Code Sequence
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_id(id: int, /) -> str:
        """
        Creates an Escape Code Sequence for the terminal color using an ID from 0 to 255.
        Use [this](https://user-images.githubusercontent.com/995050/47952855-ecb12480-df75-11e8-89d4-ac26c50e80b9.png) table to find the ID for a color.
        """
        raise NotImplementedError()

    @final
    @classmethod
    def from_hex(cls, hex: str, /) -> str:
        """
        Creates an Escape Code Sequence for the terminal color using the hexadecimal color code provided.

        ### Args:
            hex (str): hexadecimal color code

        ### Returns:
            str: Escape Code Sequence
        """
        if cls is TerminalColor:
            raise NotImplementedError(
                "TerminalColor.from_hex is not implemented. Use one of the subclasses instead."
            )
        return cls.from_rgb(*hex_to_rgb(hex))

    @final
    @classmethod
    def from_hsl(cls, h: float, s: float, l: float, /) -> str:  # noqa: E741
        """
        Creates an Escape Code Sequence for the terminal color using the HSL color provided.

        ### Args:
            h (float): hue component
            s (float): saturation component
            l (float): lightness component

        ### Returns:
            str: Escape Code Sequence
        """
        if cls == TerminalColor:
            raise NotImplementedError(
                "TerminalColor.from_hex is not implemented. Use one of the subclasses instead."
            )
        return cls.from_rgb(*tuple(map(int, hsl_to_rgb(h, s, l))))

    @final
    @staticmethod
    def from_code(code: int, /) -> str:
        """
        Creates an Escape Code Sequence for the terminal color using the ANSI Code provided.

        ### Args:
            code (int): code

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}[{code}m"

    @final
    @staticmethod
    def colorize(text: str, /, color: str) -> str:
        """
        Colorizes the specified text with the specified color and adds a RESET at the end for easier concatenation
        of multiple pieces of colored text.

        ### Args:
            text (str): The text to colorize.
            color (str): The color to use.

        ### Returns:
            str: The colorized text.
        """
        return f"{color}{text}{Modifier.RESET}"

    @final
    @staticmethod
    def brighten(color: str, /) -> str:
        """
        Brightens the specified color.
        Note that this functionality is not supported by all terminals.

        ### Args:
            color (str): The color to brighten.

        ### Returns:
            str: The brightened color.
        """
        return color.replace("[", "[1;")


def _make_color_cls(name: str, /, *, code: int):
    @final
    class __proxy__(TerminalColor):
        BLACK: Final = f"{_ESC}[{code}0m"
        RED: Final = f"{_ESC}[{code}1m"
        GREEN: Final = f"{_ESC}[{code}2m"
        YELLOW: Final = f"{_ESC}[{code}3m"
        BLUE: Final = f"{_ESC}[{code}4m"
        MAGENTA: Final = f"{_ESC}[{code}5m"
        CYAN: Final = f"{_ESC}[{code}6m"
        WHITE: Final = f"{_ESC}[{code}7m"

        DEFAULT: Final = f"{_ESC}[{code}9m"
        "Resets the color to the default and keeps any other modifiers being used."

        @override
        @staticmethod
        def from_rgb(r: int, g: int, b: int, /) -> str:
            return f"{_ESC}[{code}8;2;{r};{g};{b}m"

        @override
        @staticmethod
        def from_id(id: int, /) -> str:
            return f"{_ESC}[{code}8;5;{id}m"

    __proxy__.__name__ = name
    __proxy__.__doc__ = f"{name} colors."

    return __proxy__


Foreground = _make_color_cls("Foreground", code=3)
Background = _make_color_cls("Background", code=4)


@final
class Modifier(_Uninitiliazable, metaclass=_ImmutableMeta):
    """Color/Graphics modifiers."""

    RESET: Final = f"{_ESC}[0m"
    NONE: Final = RESET  # alias
    BOLD: Final = f"{_ESC}[1m"
    DIM: Final = f"{_ESC}[2m"
    FAINT: Final = DIM  # alias
    ITALIC: Final = f"{_ESC}[3m"
    UNDERLINE: Final = f"{_ESC}[4m"
    BLINK: Final = f"{_ESC}[5m"
    INVERSE: Final = f"{_ESC}[7m"
    HIDDEN: Final = f"{_ESC}[8m"
    INVISIBLE: Final = HIDDEN  # alias
    STRIKETHROUGH: Final = f"{_ESC}[9m"


@final
class Cursor(_Uninitiliazable, metaclass=_ImmutableMeta):
    """Cursor movement codes."""

    HOME: Final = f"{_ESC}[H"
    UP: Final = f"{_ESC}[1A"
    DOWN: Final = f"{_ESC}[1B"
    RIGHT: Final = f"{_ESC}[1C"
    LEFT: Final = f"{_ESC}[1D"

    @staticmethod
    def get_pos(file_in: TextIO = stdin, file_out: TextIO = stdout) -> tuple[int, int]:
        """
        Gets the current cursor position.\n
        Note that this functionality is not supported by all terminals.

        ### Args:
            file_in (TextIO, optional): The file to read the response from. Defaults to stdin.
            file_out (TextIO, optional): The file to write to. Defaults to stdout.

        ### Returns:
            tuple[int, int]: The current cursor position.
        """
        file_out.write(f"{_ESC}[6n")
        file_out.flush()

        buf = ""
        while (c := file_in.read(1)) != "R":
            buf += c

        return tuple(map(int, find_all(r"\d+", buf)))  # type: ignore

    @staticmethod
    def set_pos(column: int, line: int, /) -> str:
        """
        Returns the escape code sequence necessary to set the cursor position to the specified column and line.\n
        Note that this functionality is not supported by all terminals.

        ### Args:
            column (int): The column to move to.
            line (int): The line to move to.

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}[{line};{column}H"

    @staticmethod
    def up(lines: int = 1, /) -> str:
        """
        Moves cursor up by the number of lines provided.

        ### Args:
            lines (int, optional): Number of lines to move. Defaults to 1.

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}[{lines}1A"

    @staticmethod
    def down(lines: int = 1, /) -> str:
        """
        Moves cursor down by the number of lines provided.

        ### Args:
            lines (int, optional): Number of lines to move. Defaults to 1.

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}[{lines}1B"

    @staticmethod
    def right(columns: int = 1, /) -> str:
        """
        Moves cursor to the right by the number of columns provided.

        ### Args:
            columns (int, optional): Number of columns to move. Defaults to 1.

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}[{columns}1C"

    @staticmethod
    def left(columns: int = 1, /) -> str:
        """
        Moves cursor to the left by the number of columns provided.

        ### Args:
            columns (int, optional): Number of columns to move. Defaults to 1.

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}[{columns}1D"

    @staticmethod
    def save_pos(sequence: Literal["DEC", "SCO"] = "DEC") -> str:
        """
        Saves the current cursor position for use with restore_pos at a later time.

        #### Note:
        The escape sequences for "save cursor position" and "restore cursor position" were never standardised as part of
        the ANSI (or subsequent) specs, resulting in two different sequences known as "DEC" and "SCO":\n
            DEC: ESC7 (save) and ESC8 (restore)
            SCO: ESC[s (save) and ESC[u (restore)

        Different terminals (and OSes) support different combinations of these sequences (one, the other, neither or both);
        for example the iTerm2 terminal on macOS supports both, while the built-in macOS Terminal.app only supports the DEC sequences.

        #### Sources:
            https://github.com/fusesource/jansi/issues/226
            https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#:~:text=saved%20position%20(SCO)-,Note,-%3A%20Some%20sequences

        ### Args:
            sequence (Literal["DEC", "SCO"], optional): which sequence to use. Defaults to "DEC".

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}7" if sequence == "DEC" else f"{_ESC}[s"

    @staticmethod
    def restore_pos(sequence: Literal["DEC", "SCO"] = "DEC") -> str:
        """
        Restores the current cursor position, which was previously saved with save_pos.

        #### Note:
        The escape sequences for "save cursor position" and "restore cursor position" were never standardised as part of
        the ANSI (or subsequent) specs, resulting in two different sequences known as "DEC" and "SCO":\n
            DEC: ESC7 (save) and ESC8 (restore)
            SCO: ESC[s (save) and ESC[u (restore)

        Different terminals (and OSes) support different combinations of these sequences (one, the other, neither or both);
        for example the iTerm2 terminal on macOS supports both, while the built-in macOS Terminal.app only supports the DEC sequences.

        #### Sources:
            https://github.com/fusesource/jansi/issues/226
            https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#:~:text=saved%20position%20(SCO)-,Note,-%3A%20Some%20sequences

        ### Args:
            sequence (Literal["DEC", "SCO"], optional): which sequence to use. Defaults to "DEC".

        ### Returns:
            str: Escape Code Sequence
        """
        return f"{_ESC}8" if sequence == "DEC" else f"{_ESC}[u"


@final
class Erase(_Uninitiliazable, metaclass=_ImmutableMeta):
    """Erase codes."""

    CURSOR_TO_END: Final = f"{_ESC}[0J"
    CURSOR_TO_ENDL: Final = f"{_ESC}[0K"
    CURSOR_TO_LINE_END: Final = CURSOR_TO_ENDL  # alias
    CURSOR_TO_END_OF_LINE: Final = CURSOR_TO_ENDL  # alias
    START_TO_CURSOR: Final = f"{_ESC}[1K"
    START_TO_END: Final = f"{_ESC}[1J"
    SCREEN: Final = f"{_ESC}[2J"
    ALL: Final = SCREEN  # alias
    LINE: Final = f"{_ESC}[2K"

    @staticmethod
    def lines(count: int = 1, /) -> tuple[str, ...]:
        """
        Returns a tuple of escape codes to erase the specified number of lines.

        ### Args:
            count (int, optional): Number of lines to erase. Defaults to 1.

        ### Returns:
            tuple[str]: tuple of escape codes.
        """
        return tuple(Cursor.UP + Erase.LINE for _ in range(count))
