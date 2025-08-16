import importlib.metadata
import webbrowser

__version__ = importlib.metadata.version("jonathan")


def main():
    """Open Jonathan's website."""
    webbrowser.open("https://jonathangaytan.com")


if __name__ != "__main__":
    webbrowser.open("https://jonathangaytan.com")
