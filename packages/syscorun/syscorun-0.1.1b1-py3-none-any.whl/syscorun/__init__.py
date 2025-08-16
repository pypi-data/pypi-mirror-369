import sysco
from syscovis import plotter
from sysco import BaseController as Controller
from loguru import logger

# from rich.markdown import Markdown
from rich.console import Console

console = Console()

logger.debug(f"Importing {__name__}")


def main() -> None:
    console.print(
        # Markdown(
        f"# {sysco.hello_from_rust()}   ",
        style="bold white on cyan",
        # style="bold cyan on white",
        justify="center",
        # )
    )
    controller = Controller()
    try:
        controller.get_input()
    except NotImplementedError as e:
        logger.warning(f"NotImplementedError for {controller.__repr__()}")
        logger.warning(e)
        console.print(
            "You would have been better off implementing something than sleeping in class...",
            style="magenta",
        )
        pass
    plotter.plot()
