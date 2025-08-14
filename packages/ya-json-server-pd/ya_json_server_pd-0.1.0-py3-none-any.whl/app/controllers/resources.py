import json
import os

from fastapi import status

from app.config import DB_JSON_FILENAME
from app.handlers.commons import (
    convert_csv_bytes_to_json,
    retrieve_db_json_content,
    to_kebabCase,
)
from app.handlers.exceptions import APIException


def retrieve_resources_list():
    _db_json_content = retrieve_db_json_content(DB_JSON_FILENAME)
    return _db_json_content.keys()


def retrieve_resources(resource):
    _db_json_content = retrieve_db_json_content(DB_JSON_FILENAME)
    if resource not in _db_json_content:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Resourse ({resource}) not found.",
        )

    result = _db_json_content[resource]
    return result


def retrieve_resources_by_id(resource, id: int | str):
    _db_json_content = retrieve_db_json_content(DB_JSON_FILENAME)
    if resource not in _db_json_content:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Resourse ({resource}) not found.",
        )

    # Get the keys with the ID like in it, to get the first one,
    # e.g: 'id', 'idProduct', or 'productId'
    id_idx = list(
        filter(
            lambda x: x == "id"
            or (x[:2] == "id" and x[:3][-1:].isupper())
            or x[-2:] == "Id",
            _db_json_content[resource][0].keys(),
        )
    )

    resource_data = _db_json_content[resource]
    if not id_idx:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"The {resource} resourse has not an 'id' like attribute.",
        )

    id_idx_zero = id_idx[0]

    result = (
        list(filter(lambda r: r[id_idx_zero] == id, resource_data))
        if isinstance(id, str) and not id.isdigit()
        else list(filter(lambda r: r[id_idx_zero] == int(id), resource_data))
    )

    if not result:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"'{id_idx_zero}' {id} not found for the {resource} resourse.",
        )

    return result


async def update_db_json_from_csv(csv_file):
    resource = csv_file.filename
    csv_data_bytes = await csv_file.read()
    await csv_file.close()

    resource = resource[:-4] if ".csv" in resource else resource
    resource = " ".join(resource.split("_"))
    resource = to_kebabCase(resource)

    obj_json: list[dict] = convert_csv_bytes_to_json(csv_data_bytes)
    db_json_data = {
        f"{resource}": obj_json,
    }

    os.makedirs(os.path.dirname(DB_JSON_FILENAME), exist_ok=True)

    with open(DB_JSON_FILENAME, mode="w+", encoding="utf-8") as jsonfile:
        json.dump(db_json_data, jsonfile, indent=4)

    return {
        "message": "Updated DB JSON ({}) from the {} content.".format(
            DB_JSON_FILENAME, csv_file.filename
        ),
        f"{resource}": obj_json[:5],
    }
