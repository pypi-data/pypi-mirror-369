import doctyper


def main(
    name: str, email: str = doctyper.Option(..., prompt=True, confirmation_prompt=True)
):
    print(f"Hello {name}, your email is {email}")


if __name__ == "__main__":
    doctyper.run(main)
