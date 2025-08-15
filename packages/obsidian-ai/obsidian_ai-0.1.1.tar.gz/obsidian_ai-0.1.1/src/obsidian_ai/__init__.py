__all__ = ["__version__", "main"]

try:
    from importlib.metadata import PackageNotFoundError, version as _dist_version
    __version__ = _dist_version("obsidian-ai")
except Exception:
    # Fallback for local, editable, or non-installed runs
    __version__ = "0.1.1"

def main() -> None:
    """Entry point for the obsidian-ai CLI.

    Supports:
    - `obsidian-ai version` to print the package version.
    - `obsidian-ai --version` / `-V` to print the package version.
    """
    import sys

    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help", "help"}:
        print("Usage: obsidian-ai [version]")
        return

    cmd = args[0]
    if cmd in {"version", "--version", "-V"}:
        print(__version__)
        return

    print(f"Unknown command: {cmd}")
    print("Usage: obsidian-ai [version]")
