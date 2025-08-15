import doctyper
from doctyper.testing import CliRunner

from tests.assets import corner_cases as mod

runner = CliRunner()


def test_hidden_option():
    result = runner.invoke(mod.app, ["--help"])
    assert result.exit_code == 0
    assert "Say hello" in result.output
    assert "--name" not in result.output
    assert "/lastname" in result.output
    assert "TEST_LASTNAME" in result.output
    assert "(dynamic)" in result.output


def test_hidden_option_no_rich():
    rich = doctyper.core.rich
    doctyper.core.rich = None
    result = runner.invoke(mod.app, ["--help"])
    assert result.exit_code == 0
    assert "Say hello" in result.output
    assert "--name" not in result.output
    assert "/lastname" in result.output
    assert "TEST_LASTNAME" in result.output
    assert "(dynamic)" in result.output
    doctyper.core.rich = rich


def test_coverage_call():
    result = runner.invoke(mod.app)
    assert result.exit_code == 0
    assert "Hello John Doe, it seems you have 42" in result.output
