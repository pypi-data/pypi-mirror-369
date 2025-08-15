import doctyper


def main(
    name: str = doctyper.Argument("World", help="Who to greet", show_default=False),
):
    """
    Say hi to NAME very gently, like Dirk.
    """
    print(f"Hello {name}")


if __name__ == "__main__":
    doctyper.run(main)
