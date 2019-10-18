from os import makedirs, listdir, path
import re
from typing import List


# for now
Path = str


def create_folder(directory: Path) -> Path:
    if not path.exists(directory):
        makedirs(directory, exist_ok=True)
    elif not path.isdir(directory):
        raise ValueError(("Attempt to create {}, which already exists " +
                          "but is not a directory").format(directory))
    return directory


def list_files(dir: Path, regexp: str = '.*') -> List[Path]:
    if not path.isdir(dir):
        raise Exception('Cannot list files: "' + dir + '" is not a ' +
                        'directory or does not exist')

    expr = re.compile(regexp, re.M)
    files = []  # type: List[Path]
    for file in listdir(dir):
        file_path = path.join(dir, file)
        if not path.isfile(file_path):
            continue
        if expr.search(file):
            files.append(Path(file_path))
    return files
