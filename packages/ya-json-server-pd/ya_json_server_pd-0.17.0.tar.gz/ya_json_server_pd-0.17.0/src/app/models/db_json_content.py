import json
import os

from app.config import DB_JSON_FILENAME


class JsonContentModel:
    _json_data: dict

    def __init__(self, db_json_filename: str):
        self._db_json_filename = db_json_filename
        self._retrieve_db_json_content()

    def _init_db_json(self):

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

    def get_resources_list(self):
        resources = self._json_data.keys()

        result = [{resource: len(self._json_data[resource])} for resource in resources]

        return result

    def get_data_by_resource_name(self, resource, page, limit):
        if resource not in self._json_data:
            return {}
        result = self._json_data[resource]

        low_limit = page * limit - limit
        high_limit = page * limit - 1
        result = result[low_limit:high_limit]

        return result

    def get_data_resource_by_id(
        self, resource: str, id: int | str
    ) -> bool | None | dict:
        """
        Returns:
            - bool | None | dict: _Returns `False` if resource not found or
                `None` if resourse has not an 'id' like attribute._
        """
        if resource not in self._json_data:
            return False
        # Get the keys with the ID like in it, to get the first one,
        # e.g: 'id', 'idProduct', or 'productId'
        id_idx = list(
            filter(
                lambda x: x == "id"
                or (x[:2] == "id" and x[:3][-1:].isupper())
                or x[-2:] == "Id",
                self._json_data[resource][0].keys(),
            )
        )
        if not id_idx:
            return None

        id_idx_zero = id_idx[0]
        resource_data = self._json_data[resource]

        result = (
            list(filter(lambda r: r[id_idx_zero] == id, resource_data))
            if isinstance(id, str) and not id.isdigit()
            else list(filter(lambda r: r[id_idx_zero] == int(id), resource_data))
        )

        return result

    def set(self, json_data):
        self._json_data = json_data

    def _retrieve_db_json_content(self):
        if not os.path.exists(self._db_json_filename):
            self._init_db_json()
        with open(self._db_json_filename, mode="r") as db_json:
            self._json_data: dict[list[dict]] = json.load(db_json)

        return self._json_data
        return self._json_data
