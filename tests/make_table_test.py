import os
import sys

from src import create_table
from src import log, TABLE_NAME


if __name__ == '__main__':
    try:
        path_to_save_directory = sys.argv[1]
        if not os.path.exists(path_to_save_directory):
            log.error("The path %s is not a real path", path_to_save_directory)
            sys.exit(2)
    except IndexError:
        log.error("You need to provide a path to a table!")
        sys.exit(2)

    create_table([["Ivan", "34", "url", "None"]], os.path.join(path_to_save_directory, TABLE_NAME))
