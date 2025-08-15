import toml


def read_file(path: str):
    """Read a file and return the content.

    :param path: _description_
    :type path: str
    """
    with open(path, encoding="utf8") as file:
        file_content = file.read()
    return file_content


def write_to_file(path: str, content):
    """Write given content to the path.

    :param path: _description_
    :type path: str
    :param content: _description_
    :type content: _type_
    """
    with open(path, "w", encoding="utf8") as fhh:
        fhh.write(content)


def read_toml(path):
    with open(path, encoding="utf8") as file:
        content = toml.load(file)
    return content


def write_to_toml(path: str, content):
    with open(path, "w", encoding="utf8") as file:
        toml.dump(content, file)
