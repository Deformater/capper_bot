def name_validation(name: str) -> bool:
    if len(name.split()) != 4 or len(name) > 255:
        return False

    name, surname, patronymic, group = name.split()

    return f"{name}{surname}{patronymic}".isalpha() and group.isalnum()


def stream_validation(stream: str) -> bool:
    if len(stream.split(".")) != 2 or len(stream) > 20:
        return False

    stream1, stream2 = stream.split(".")

    return f"{stream1}{stream2}".isnumeric()
