"""CLI for tap-canvas."""

from tap_canvas.tap import TapCanvas

def cli():
    """Run the tap CLI."""
    TapCanvas.cli()

if __name__ == "__main__":
    cli()