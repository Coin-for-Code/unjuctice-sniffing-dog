import os.path

import requests
import json

url = "https://corruptinfo.nazk.gov.ua/ep/1.0/corrupt/getAllData"


if __name__ == '__main__':

    if not os.path.isfile("archive_cache.json"):
        print("No cached file was found.")
        print("Requesting the data")
        response = requests.get(url)
        print("Converting it to dict")
        archived_text = response.json()
        print(archived_text)
        with open("archive_cache.json", "w") as archive:
            archive.write(archived_text)
    else:
        print("Taking the cached archive")

    names = []

    with open("archive_cache.json", "r") as archived_file:
        archive = json.load(archived_file)
        for record in archive:
            last_name = record["indLastNameOnOffenseMoment"]
            family_name = record["indFirstNameOnOffenseMoment"]
            papa_name = record["indPatronymicOnOffenseMoment"]
            names.append(last_name+family_name+papa_name)




