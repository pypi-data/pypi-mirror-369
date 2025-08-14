# Yet Another JSON Server

[![image](https://gitlab.com/adrianovieira/ya-json-server-pd/badges/main/pipeline.svg)](https://gitlab.com/adrianovieira/ya-json-server-pd/-/pipelines)
[![image](https://gitlab.com/adrianovieira/ya-json-server-pd/badges/main/coverage.svg?job=job::tests::api&key_text=coverage)](https://gitlab.com/adrianovieira/ya-json-server-pd/-/jobs/artifacts/main/browse?job=job::tests::api)

## Introduction

A mock REST API with zero coding.

Technologies::
* Python 3.13+
* FastAPI 0.116+

## Getting started

### Making requests

Check the [OpenAPI](https://gitlab.com/adrianovieira/ya-json-server-pd/-/blob/main/docs/openapi.json) description to learn how to make requests
to it.

You can use de docker image from the project, e.g.:

```shell
docker run --rm -it -p 80:8000 registry.gitlab.com/adrianovieira/ya-json-server-pd:v1.0
```

Therefore, access API at http://api.localhost

## Contributions

```bash
pipenv install --dev
```

*`.env`* setup::
* Use `env.example` as reference

```shell
PYTHONPATH=:src:src/app:
PYTHONDONTWRITEBYTECODE=1
APP_JSON_FILENAME=my-db.json # (optional) default: data/db.json
```

Update the `.env` with the `APP_JSON_FILENAME` environment variable if you wanna
change de file name, e.g.:

```shell
APP_JSON_FILENAME=my-db.json
```

Execute in dev mode::

```shell
pipenv run dev
```

Access the API on http://localhost:8000[]

Tests::

```
pipenv run tests
```

> The projects [json-server](https://github.com/typicode/json-server) and 
[Python JSON Server](https://github.com/ganmahmud/python-json-server) inspires this one.

## License

> link:LICENSE[Apache License 2.0]