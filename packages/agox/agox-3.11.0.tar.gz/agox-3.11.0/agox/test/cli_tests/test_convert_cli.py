from pathlib import Path

from click.testing import CliRunner

from agox.cli.main import main
from agox.test.test_utils import TemporaryFolder


def test_convert_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["convert", "--help"])
    assert result.exit_code == 0


def test_convert_cli(tmpdir: Path, database_file_path: Path) -> None:
    with TemporaryFolder(tmpdir):
        runner = CliRunner()
        result = runner.invoke(main, ["convert", str(database_file_path.resolve()), "--name", "converted.traj"])
        assert result.exit_code == 0
