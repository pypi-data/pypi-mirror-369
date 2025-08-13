# Developer guide

## Run tests

```console
uv run pytest --cov
```

## Generate Python bindings

```console
uv run datamodel-codegen --use-standard-collections --input src/commandfile/data/schema.json --input-file-type jsonschema --output src/commandfile/model_generated.py
```
