def check_str(string: str, name: str = None) -> bool:
    if not name:
        name = "value"

    if string is None:
        raise ValueError(f"{name} is none")

    if not isinstance(string, str):
        raise ValueError(f"{name} is not a string")

    if len(string) == 0:
        raise ValueError(f"{name} is empty")
