import json
import os
import string
from io import BytesIO
from re import sub

import pandas as pd
from unidecode import unidecode

from app.config import DB_JSON_FILENAME


def to_camelCase(statement: str):
    """_Convert statement string in camel case (camelCase) convention._

    example:
    - from: `'Suspéndisse dictum diam àc magna varius, in susçipit elit luctus?'`
    - into: `'suspendisseDictumDiamAcMagnaVariusInSuscipitElitLuctus'`
    """
    statement = unidecode(statement)
    statement = statement.translate(str.maketrans("", "", string.punctuation))
    statement = sub(r"(_|-)+", " ", statement).title().replace(" ", "")
    return statement[0].lower() + statement[1:]


def to_kebabCase(statement: str):
    """_Convert statement string in kebab case (kebab-case) convention._

    example:
    - from: `'Suspéndisse dictum diam àc Magna varius, in susçipit elit Luctus?'`
    - into: `'suspendisse-dictum-diam-ac-magna-varius-in-suscipit-elit-luctus'`
    """
    statement = unidecode(statement)
    statement = statement.translate(str.maketrans(" ", "-", string.punctuation))
    return statement.lower()


def convert_csv_bytes_to_json(csv_data):
    """_Convert csv data into json._

    Keyword arguments:
    - csv_data -- the csv content
    """
    data_frame = pd.read_csv(BytesIO(csv_data))
    columns_new_names = {c: to_camelCase(c) for c in data_frame.columns}
    data_frame = data_frame.rename(columns=columns_new_names)
    obj_data_json = json.loads(data_frame.to_json(orient="records"))

    return obj_data_json


def retrieve_db_json_content(db_json_filename: str):
    with open(db_json_filename, mode="r") as db_json:
        json_content: dict[list[dict]] = json.load(db_json)

    return json_content


def init_db_json():

    db_sample_if_not_exists = {
        "yetAnotherJsonServerSample": [
            {
                "id": 1,
                "company": "Chang-Fisher",
                "city": "Tammyfort",
                "country": "Iraq",
                "postcode": 40256,
                "pricetag": "45,593.82",
            },
            {
                "id": 2,
                "company": "Montgomery LLC",
                "city": "West Corey",
                "country": "Barbados",
                "postcode": 90152,
                "pricetag": "7778.15",
            },
            {
                "id": 3,
                "company": "Bowman, Harris and Tran",
                "city": "Grimesview",
                "country": "Bahamas",
                "postcode": 72420,
                "pricetag": "91.60",
            },
        ]
    }

    if not os.path.exists(DB_JSON_FILENAME):
        os.makedirs(name=os.path.dirname(DB_JSON_FILENAME), exist_ok=True)
        with open(DB_JSON_FILENAME, mode="w+") as jsonfile:
            json.dump(db_sample_if_not_exists, jsonfile, indent=4)
