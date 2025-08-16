from syscovis.plotter.plotter import Plotter
from loguru import logger

logger.debug(f"Importing {__name__}")

plotter = Plotter()


def hello() -> str:
    return "Hello from syscovis!"
