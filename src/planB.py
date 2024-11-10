import os.path
import sys

import requests
import json
import csv

from src.utils import TABLE_NAME
from src.utils import log

url = "https://corruptinfo.nazk.gov.ua/ep/1.0/corrupt/getAllData"


if __name__ == '__main__':

    # Configure the save folder
    if len(sys.argv) <= 1:
        log.error("You need to provide a path to the save folder!")
        sys.exit(2)

    if not os.path.exists(sys.argv[1]):
        log.error("The given path is empty!")
        sys.exit(2)

    path_to_save_dir = sys.argv[1]

    path_to_archived_cache = os.path.join(path_to_save_dir, "archive_cache.json")
    # Retrieve the names
    if not os.path.isfile(path_to_archived_cache):
        log.info("No cached file was found.")
        log.info("Requesting the data")
        response = requests.get(url)
        log.info("Converting it to dict")
        archived_text = response.json()
        with open(path_to_archived_cache, "w") as archive:
            archive.write(archived_text)
            log.info("Cached the archive into %s", path_to_archived_cache)
    else:
        log.info("Taking the cached archive from %s", path_to_archived_cache)

    names = []

    log.info("Extracting the names")
    with open(path_to_archived_cache, "r") as archived_file:
        archive = json.load(archived_file)
        for record in archive:
            last_name = record["indLastNameOnOffenseMoment"]
            family_name = record["indFirstNameOnOffenseMoment"]
            papa_name = record["indPatronymicOnOffenseMoment"]
            names.append(last_name+family_name+papa_name)

    table = []
    # Open processed file
    with open(TABLE_NAME, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            table.append([row[0], row[1]])





