import jsonschema, json, os
from referencing import Registry
from referencing.jsonschema import DRAFT202012
from pathlib import Path

"""
Allows types to be defined as json schema as in-memory schemas or loaded
into a registry from .json files and then used for validation.

You can either use the validator's .validate() method or pass the validator
to this module's validated() method for added error handling and so you can
call validated code like this:
```
validatedEventBody = validated(eventBody, validator=validators['eventBodyValidator'])
# OR
validatedEventBody = validated(eventBody, schema=eventBodySchema)
```

You can use composed schemas when validating if you use the validator for a
schema that depends on other schemas with $ref. Specifically this would be the
validator returned from `validatorRegistryFromSchemasDirectory()` after loading
schemas from a directory.
"""

# TODO: Can you crawl the registry to return resolved composed shcemas?

def validatorRegistryFromSchemasDirectory(jsonSchemaDirectory):
    modelFiles = [''.join(d.split('.json')) for d in os.listdir(jsonSchemaDirectory) if d.split('.')[-1] == 'json']
    registerthis = [
        (modelFile, DRAFT202012.create_resource(json.loads(Path(f'{jsonSchemaDirectory}/{modelFile}.json').read_text())))
        for modelFile in modelFiles
    ]
    registry = Registry().with_resources(registerthis)
    validators = dict([
        (modelFile,jsonschema.Draft202012Validator(registry.contents(modelFile),registry=registry))
        for modelFile in modelFiles
    ])
    return validators

class DataValidationError(Exception):
    pass

def validated(obj, schema = {}, validator = {}):
    try:
        if schema:
            jsonschema.validate(
                instance=obj,
                schema=schema
            )
        if validator:
            validator.validate(obj)
    except jsonschema.exceptions.ValidationError as e:
        raise DataValidationError(
            f'Data does not match the provided schema. Validation errors: {e}'
        ) from None
    except Exception as e:
        raise Exception(
            f'{__name__}: unhandled error in validator: {e}'
        )
    return obj

if __name__ == '__main__':
    validators = validatorRegistryFromSchemasDirectory('validatorTestModels')