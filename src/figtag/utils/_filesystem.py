from os import path
from os import makedirs

# for now
Path = str


def create_folder(directory: Path) -> Path:
    if not path.exists(directory):
        makedirs(directory, exist_ok=True)
    elif not path.isdir(directory):
        raise ValueError(("Attempt to create {}, which already exists " +
                          "but is not a directory").format(directory))
    return directory
