"""
Launches the GUI application
"""

from .gui.main import app, setup_logging
from flaskwebgui import FlaskUI


def main():
    """
    Entry point for the GUI console script.
    """
    setup_logging()
    FlaskUI(
        app=app,
        server="fastapi",
        fullscreen=False,
        width=1200,
        height=800
    ).run()


if __name__ == "__main__":
    main()
