"""
SPARKY ASCII Art Banner
Beautiful robot dog + SPARKY logo for CLI applications
"""

# Rich-formatted ASCII banner
RICH_ASCII_LAYOUT = r"""
            __                  ███████ ██████   █████  ██████  ██   ██ ██    ██
        .-''  ''-.              ██      ██   ██ ██   ██ ██   ██ ██  ██   ██  ██
       /        o\__            ███████ ██████  ███████ ██████  █████     ████
      |           ___)               ██ ██      ██   ██ ██   ██ ██  ██     ██
       \_\__)_____)             ███████ ██      ██   ██ ██   ██ ██   ██    ██
       /     \     \
      |       |    |
       \_____/ \___/
        |  |   |  |
       (_)(_) (_)(_)                          [bold cyan]SPARKY CLI[/bold cyan]  •  [bold green]v0.0.2[/bold green]
"""


def get_banner() -> str:
    """Get the SPARKY ASCII banner"""
    return RICH_ASCII_LAYOUT


def print_banner():
    """Print the banner to console using rich"""
    try:
        from rich.console import Console

        console = Console()
        console.print(RICH_ASCII_LAYOUT)
        console.print(
            "[bold green]Welcome to Sparky CLI! Ready to roll.[/bold green]\n"
        )
    except ImportError:
        # Fallback to plain text if rich is not available
        import re

        plain_banner = re.sub(r"\[.*?\]", "", RICH_ASCII_LAYOUT)
        print(plain_banner)
        print("Welcome to Sparky CLI! Ready to roll.\n")


if __name__ == "__main__":
    print_banner()
