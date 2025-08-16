import rich_click as click

from agox.cli.cli_analysis import cli_analysis
from agox.cli.cli_convert import cli_convert
from agox.cli.cli_graph_sorting import cli_graph_sorting
from agox.cli.cli_notebook import cli_notebook
from agox.cli.cli_plot import cli_plot


@click.group(name="agox")
@click.version_option()
def main() -> None:
    """
    Command line interface for AGOX.
    """
    return None


main.add_command(cli_convert)
main.add_command(cli_notebook)
main.add_command(cli_graph_sorting)
main.add_command(cli_analysis)
main.add_command(cli_plot)
