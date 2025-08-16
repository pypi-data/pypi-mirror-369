from pathlib import Path

from click.testing import CliRunner

from agox.cli.main import main
from agox.test.test_utils import TemporaryFolder


def test_plot_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["plot", "--help"])
    assert result.exit_code == 0


def test_plot_cli_database(database_file_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["plot", str(database_file_path.resolve()), "--backend", "agg"])
    assert result.exit_code == 0


def test_plot_cli_trajectory(trajectory_file_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["plot", str(trajectory_file_path.resolve()), "--backend", "agg"])
    assert result.exit_code == 0


def test_plot_cli_save(tmpdir, database_file_path: Path) -> None:
    with TemporaryFolder(tmpdir):
        output = "fig.png"
        runner = CliRunner()
        result = runner.invoke(
            main, ["plot", str(database_file_path.resolve()), "--backend", "agg", "--output", output]
        )

        assert Path(output).exists()

    assert result.exit_code == 0
