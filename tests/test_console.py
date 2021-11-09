import click.testing

from mediasorter import console


def test_main_succeeds():
    runner = click.testing.CliRunner()
    result = runner.invoke(
        console.main  # , ["-s", "/c/Users/srao/Desktop/source", "-t", "/tmp"]
    )
    assert result.exit_code == 0
