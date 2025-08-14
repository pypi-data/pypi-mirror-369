"""Terminal color utilities."""


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_colored(text: str, color: str) -> None:
    """Print colored text to terminal."""
    print(f"{color}{text}{Colors.ENDC}")


def print_header(text: str) -> None:
    """Print a header with formatting."""
    print()
    print_colored("=" * 60, Colors.HEADER)
    print_colored(text.center(60), Colors.HEADER + Colors.BOLD)
    print_colored("=" * 60, Colors.HEADER)
    print()
