from pathlib import Path

from click.testing import CliRunner

from agox.cli.main import main
from agox.test.test_utils import TemporaryFolder


def test_plot_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["graph-sort", "--help"])
    assert result.exit_code == 0


def test_graph_sort_database(tmpdir: Path, database_directories: Path) -> None:
    with TemporaryFolder(tmpdir):
        runner = CliRunner()
        result = runner.invoke(main, ["graph-sort", "-d", str(database_directories[0].resolve())])
        assert result.exit_code == 0


def test_graph_sort_trajectory(tmpdir: Path, trajectory_file_path: Path) -> None:
    with TemporaryFolder(tmpdir):
        runner = CliRunner()
        result = runner.invoke(main, ["graph-sort", "-t", str(trajectory_file_path.resolve())])
        assert result.exit_code == 0
