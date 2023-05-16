from sys import platform


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ONE = ''


class WinColors:
    HEADER = ''
    BLUE = ''
    CYAN = ''
    GREEN = ''
    WARNING = ''
    FAIL = ''
    END = ''
    BOLD = ''
    UNDERLINE = ''
    ONE = ''


if platform.startswith('win'):
    c = WinColors()
else:
    c = Colors()
