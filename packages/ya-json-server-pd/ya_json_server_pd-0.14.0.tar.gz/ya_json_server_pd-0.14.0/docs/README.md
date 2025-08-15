# Yet Another JSON Server

[![image](https://gitlab.com/adrianovieira/ya-json-server-pd/badges/main/pipeline.svg)](https://gitlab.com/adrianovieira/ya-json-server-pd/-/pipelines)
[![image](https://gitlab.com/adrianovieira/ya-json-server-pd/badges/main/coverage.svg?job=job::tests::api&key_text=coverage)](https://gitlab.com/adrianovieira/ya-json-server-pd/-/jobs/artifacts/main/browse?job=job::tests::api)

## Introduction

A REST API for JSON content with zero coding.

Technologies::

- Python 3.13+
- FastAPI 0.116+

## Getting started

### Making requests

| endpoints              | summary                                    |
| ---------------------- | ------------------------------------------ |
| `GET /`                | Get list of resources.                     |
| `GET /{resource}`      | Get all the data of the resource.          |
| `GET /{resource}/{id}` | Get the resource ID data.                  |
| `PUT /upload`          | Update DB JSON file from CSV file content. |
| `...`                  |

Check the [OpenAPI](https://gitlab.com/adrianovieira/ya-json-server-pd/-/blob/main/docs/openapi.json)
documentation to read the full description for each endpoint.

You can use de docker image from the project, e.g.:

```shell
docker run --rm -it -p 80:8000 registry.gitlab.com/adrianovieira/ya-json-server-pd:v1.0
```

This way, you can access the documentation for the running API at
http://api.localhost/docs

## License

> Apache License 2.0
