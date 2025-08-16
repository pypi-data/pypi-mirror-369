from pathlib import Path

from rich.console import Console
# from loguru import logger

console = Console()
# console = Console(record=True)
# console = Console(theme=)
# logger.debug(f"Importing {__name__}")


class Plotter:
    def __init__(
        self, save=True, show=True, name="", root_indicator="toml", plot_dir="plots"
    ):
        console.print(
            "Initialize plotter...",
            end=" ",
            style="bold cyan",
        )
        self.save: bool = save
        self.show: bool = show
        self.root_indicator: str = root_indicator
        self.project_root_dir: Path = Plotter.find_project_root()
        self.plot_dir: Path = self.create_plot_dir(plot_dir)
        self.task_name: str = name
        console.print(
            "PLOTTER IS READY TO PLOT",
            # style="bold white on cyan",
            # style="bold cyan on white",
            style="bold blink cyan on white",
            justify="center",
        )
        # TODO: save console output from plotter (or other instance)
        # console.print("plotter is ready to plot...", style="bold cyan")
        # console.save_svg("plots/plotter.svg")
        # console.save_html("plots/plotter.html")

    @staticmethod
    def find_project_root(indicator="toml") -> Path:
        """
        Find project root for relative paths
        """
        # TODO: make indicator to enum
        root_indicators = {
            "toml": "pyproject.toml",
            "git": ".git",
            "venv": ".venv",
        }
        # select indicator, use pyproject.toml as fallback
        indicator_path = root_indicators.get(indicator, "pyproject.toml")
        # indicator_path = "bla"
        # set current location as start
        run_dir = Path.cwd()
        current_dir = run_dir
        # follow the path backwards
        while current_dir != current_dir.parent:
            if (current_dir / indicator_path).exists():
                break
            current_dir = current_dir.parent
        if current_dir != Path("/"):
            console.print("Project root found!", end=" ", style="green")
            # console.print(current_dir, style="white", emoji=True)
            return current_dir
        else:
            console.print("Project root not found!", style="magenta bold")
            console.print(f"Set [cwd = {run_dir}] as project root", style="yellow")
            return run_dir

    def create_plot_dir(self, plot_dir: str) -> Path:
        plot_path = self.project_root_dir / Path(plot_dir)
        console.print(f"set path for plots: {plot_path}", style="white italic")
        plot_path.mkdir(parents=True, exist_ok=True)
        return plot_path

    def plot(self, plot_name="task_ .jpg"):
        plot_path = self.plot_dir / plot_name
        print(f"save plot to {plot_path}")
