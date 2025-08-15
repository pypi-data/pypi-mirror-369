import doctyper
from typing_extensions import Annotated


def main(
    name: str,
    email: Annotated[str, doctyper.Option(prompt=True, confirmation_prompt=True)],
):
    print(f"Hello {name}, your email is {email}")


if __name__ == "__main__":
    doctyper.run(main)
