from click.testing import CliRunner

from agox.cli.main import main


def test_main_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
