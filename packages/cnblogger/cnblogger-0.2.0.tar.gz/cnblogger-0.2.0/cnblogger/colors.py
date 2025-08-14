from __future__ import annotations

from typing import Dict

try:
	from colorama import Fore, Style, init as colorama_init  # type: ignore
	colorama_init(autoreset=True)
	_RESET = Style.RESET_ALL
	_NAME_TO_FORE: Dict[str, str] = {
		"black": Fore.BLACK,
		"red": Fore.RED,
		"green": Fore.GREEN,
		"yellow": Fore.YELLOW,
		"blue": Fore.BLUE,
		"magenta": Fore.MAGENTA,
		"cyan": Fore.CYAN,
		"white": Fore.WHITE,
		"bright_black": Fore.LIGHTBLACK_EX,
		"bright_red": Fore.LIGHTRED_EX,
		"bright_green": Fore.LIGHTGREEN_EX,
		"bright_yellow": Fore.LIGHTYELLOW_EX,
		"bright_blue": Fore.LIGHTBLUE_EX,
		"bright_magenta": Fore.LIGHTMAGENTA_EX,
		"bright_cyan": Fore.LIGHTCYAN_EX,
		"bright_white": Fore.LIGHTWHITE_EX,
	}
except Exception:
	# Fallback: no colors if colorama is not available
	_RESET = ""
	_NAME_TO_FORE = {}


def colorize(text: str, color_name: str) -> str:
	color = _NAME_TO_FORE.get(color_name.lower(), "")
	if not color:
		return text
	return f"{color}{text}{_RESET}"
