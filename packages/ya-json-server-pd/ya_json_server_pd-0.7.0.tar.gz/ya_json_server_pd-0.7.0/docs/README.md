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

This way, you can access the documentation for the running API at
http://api.localhost/docs

## License

> Apache License 2.0