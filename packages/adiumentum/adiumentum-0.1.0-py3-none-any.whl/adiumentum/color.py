class Colorizer:
    def __init__(self, use_colors: bool = True) -> None:
        if use_colors:
            self.BLACK = "\u001b[30m"
            self.RED = "\u001b[31m"
            self.GREEN = "\u001b[32m"
            self.YELLOW = "\u001b[33m"
            self.BLUE = "\u001b[34m"
            self.MAGENTA = "\u001b[35m"
            self.CYAN = "\u001b[36m"
            self.WHITE = "\u001b[37m"
            self.RESET = "\u001b[0m"
        else:
            self.BLACK = ""
            self.RED = ""
            self.GREEN = ""
            self.YELLOW = ""
            self.BLUE = ""
            self.MAGENTA = ""
            self.CYAN = ""
            self.WHITE = ""
            self.RESET = ""

    @staticmethod
    def strip(s: str) -> str:
        return s[5:-4] if s.startswith("\u001b") else s

    def length(self, s: str) -> int:
        return len(self.strip(s))

    def black(self, text: str) -> str:
        return self._format(text, self.BLACK)

    def red(self, text: str) -> str:
        return self._format(text, self.RED)

    def green(self, text: str) -> str:
        return self._format(text, self.GREEN)

    def yellow(self, text: str) -> str:
        return self._format(text, self.YELLOW)

    def blue(self, text: str) -> str:
        return self._format(text, self.BLUE)

    def magenta(self, text: str) -> str:
        return self._format(text, self.MAGENTA)

    def cyan(self, text: str) -> str:
        return self._format(text, self.CYAN)

    def white(self, text: str) -> str:
        return self._format(text, self.WHITE)

    def _format(self, text: str, color_code: str) -> str:
        return f"{color_code}{text}{self.RESET}"
