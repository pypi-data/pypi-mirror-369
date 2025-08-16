import importlib.metadata
import webbrowser

__version__ = importlib.metadata.version("jonathan")

# Guard to ensure website only opens once per process
_website_opened = False

def main():
    """Open Jonathan's website."""
    global _website_opened
    if not _website_opened:
        webbrowser.open("https://jonathangaytan.com")
        _website_opened = True


if __name__ != "__main__":
    main()
