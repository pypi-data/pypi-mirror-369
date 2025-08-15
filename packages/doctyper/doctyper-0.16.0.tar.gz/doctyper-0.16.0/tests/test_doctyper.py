import re
import typing
from typing import TYPE_CHECKING, Any, Sequence, Type

import doctyper
import pytest
import typing_extensions
from doctyper._typing import Annotated, Callable, Literal
from doctyper.testing import CliRunner

if TYPE_CHECKING:
    from typing import Literal

runner = CliRunner()


def assert_run(
    args: Sequence[str],
    code: int,
    expected: str,
    func: Callable[..., None],
    regex: bool = True,
) -> None:
    app = doctyper.SlimTyper()
    app.command()(func)
    result = runner.invoke(app, args)
    assert result.exit_code == code
    if regex:
        assert re.search(expected, result.stdout)
    else:
        assert expected in result.stdout


def assert_help(expected: str, func: Callable[..., None]) -> None:
    assert_run(["--help"], 0, expected, func)


def test_slim_typer():
    app = doctyper.SlimTyper()

    assert isinstance(app, doctyper.Typer)
    assert not app.pretty_exceptions_enable
    assert not app._add_completion


def test_doc_argument():
    def main(arg: str):
        """Docstring.

        Args:
            arg: String Argument.
        """

    assert_help(r"arg\s+TEXT\s+String Argument\. \[required\]", main)


def test_doc_option():
    def main(opt: str = 1):
        """Docstring.

        Args:
            opt: String Option with Default.
        """

    assert_help(r"--opt\s+TEXT\s+String Option with Default\. \[default: 1\]", main)


def test_doc_flag():
    def main(flag: bool = True):
        """Docstring.

        Args:
            flag: Boolean Flag with Default.
        """

    assert_help(
        r"--flag\s+--no-flag\s+Boolean Flag with Default\. \[default: flag\]",
        main,
    )


def test_choices_help():
    def main(choice: Literal["a", "b"]):
        """Docstring.

        Args:
            choice: The valid choices.
        """

    assert_help(r"choice\s+CHOICE:\{a\|b\}\s+The valid choices\. \[required\]", main)


def test_choices_non_string():
    def main(choice: Literal[1, 2]): ...

    with pytest.raises(TypeError, match="Literal values must be strings"):
        assert_help("", main)


def test_choices_valid_value():
    def main(choice: Literal["a", "b"]):
        print("The choice was", choice)

    assert_run(["b"], 0, "The choice was b", main, regex=False)


def test_choices_invalid_value():
    app = doctyper.SlimTyper()

    @app.command()
    def main(choice: Literal["a", "b"]): ...

    assert_run(
        ["c"],
        2,
        "Invalid value for 'CHOICE:{a|b}': 'c' is not one of 'a', 'b'.",
        main,
        regex=False,
    )


def test_choices_help_list():
    def main(choice: list[Literal["a", "b"]]):
        """Docstring.

        Args:
            choice: The valid choices.
        """

    assert_help(
        r"choice\s+CHOICE:\{a\|b\}\.\.\.\s+The valid choices\. \[required\]", main
    )


def test_choices_help_tuple():
    def main(choice: tuple[Literal["a", "b"], int]):
        """Docstring.

        Args:
            choice: Tuple with 'a'/'b' and an int.
        """

    assert_help(
        r"choice\s+CHOICE\.\.\.\s+Tuple with 'a'/'b' and an int\. \[required\]", main
    )


def test_choices_union():
    def main(choice: Literal["a"] | Literal["b"]):
        """Docstring.

        Args:
            choice: The valid choices.
        """

    assert_help(r"choice\s+CHOICE:\{a\|b\}\s+The valid choices\. \[required\]", main)


def test_choices_union_error():
    def main(choice: Literal["a"] | str): ...

    with pytest.raises(
        AssertionError, match="Typer Currently doesn't support Union types"
    ):
        assert_help("", main)


def test_future_annotations():
    def main(
        opt: "str | None" = None,  # future annotation would convert str | None to "str | None"
    ): ...

    assert_help(r"--opt\s+TEXT\s+\[default: None\]", main)


def test_future_annotations_with_docstring():
    def main(
        opt: "str | None" = None,  # future annotation would convert str | None to "str | None"
    ):
        """Docstring.

        Args:
            opt: String Option with Default.
        """

    assert_help(r"--opt\s+TEXT\s+String Option with Default\. \[default: None\]", main)


def test_help_preference():
    def main(
        doc_opt: Annotated[str, doctyper.Option()] = "string",
        ann_opt: Annotated[
            str, doctyper.Option(help="String Option with Annotated Help.")
        ] = "string",
    ):  # future annotation would convert str | None to "str | None"
        """Docstring.

        Args:
            doc_opt: String Option with Docstring Help.
            ann_opt: Not shown in help.
        """

    assert_help(
        r"--doc-opt\s+TEXT\s+String Option with Docstring Help\. \[default: string\]",
        main,
    )
    assert_help(
        r"--ann-opt\s+TEXT\s+String Option with Annotated Help\. \[default: string\]",
        main,
    )


def test_custom_annotated():
    def main(
        opt: Annotated["str | None", doctyper.Option(show_default="Custom")] = None,
    ):  # future annotation would convert str | None to "str | None"
        """Docstring.

        Args:
            opt: String Option with Custom Default.
        """

    assert_help(
        r"--opt\s+TEXT\s+String Option with Custom Default\. \[default: \(Custom\)\]",
        main,
    )


@pytest.mark.parametrize(
    "type_",
    [
        pytest.param(
            typing_extensions.TypeAliasType, id="typing_extensions.TypeAliasType"
        ),
        pytest.param(
            getattr(typing, "TypeAliasType", None),
            marks=pytest.mark.skipif(
                not hasattr(typing, "TypeAliasType"),
                reason="TypeAliasType is not available",
            ),
            id="typing.TypeAliasType",
        ),
    ],
)
def test_typing_type_alias(type_: Type[Any]):
    Alias = type_("Alias", Literal["a", "b"])

    def main(arg: Alias):
        """Docstring.

        Args:
            arg: Aliased argument.
        """

    assert_help(r"arg\s+ARG:{a\|b}\s+Aliased argument\. \[required\]", main)


@pytest.mark.parametrize(
    "type_",
    [
        pytest.param(typing_extensions.Annotated, id="typing_extensions.Annotated"),
        pytest.param(
            getattr(typing, "Annotated", None),
            marks=pytest.mark.skipif(
                not hasattr(typing, "Annotated"), reason="Annotated is not available"
            ),
            id="typing.Annotated",
        ),
    ],
)
def test_typing_annotated(type_: Type[Any]):
    def main(
        ann_arg: type_[str, doctyper.Argument(help="Annotated Argument.")],
    ): ...

    assert_help(
        r"ann_arg\s+TEXT\s+Annotated Argument\. \[required\]",
        main,
    )


@pytest.mark.parametrize(
    "type_",
    [
        pytest.param(typing_extensions.Literal, id="typing_extensions.Literal"),
        pytest.param(
            getattr(typing, "Literal", None),
            marks=pytest.mark.skipif(
                not hasattr(typing, "Literal"), reason="Literal is not available"
            ),
            id="typing.Literal",
        ),
    ],
)
def test_typing_literal(type_: Type[Any]):
    def main(choice: type_["a", "b"]): ...  # noqa: F821

    assert_help(r"choice\s+CHOICE:\{a\|b\}\s+\[required\]", main)
