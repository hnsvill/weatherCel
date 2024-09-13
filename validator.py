import jsonschema, json, os
from referencing import Registry
from referencing.jsonschema import DRAFT202012

jsonSchemasDir = 'model'
modelFiles = [''.join(d.split('.json')) for d in os.listdir('model') if d.split('.')[-1] == 'json'] 
registerthis = [
    (mf, DRAFT202012.create_resource(json.load(open(f'{jsonSchemasDir}/{mf}.json','r'))))
    for mf in modelFiles
]
registry = Registry().with_resources(registerthis)
validators = dict([
    (mf,jsonschema.Draft202012Validator(registry.contents(mf),registry=registry))
    for mf in modelFiles
])

print(validators['latlonSchema'])

class DataValidation(Exception):
    pass

class ComeCreateANewCase(Exception):
    pass

def validated(obj, schema):
    try:
        jsonschema.validate(
            instance=obj,
            schema=schema
        )
    except jsonschema.exceptions.ValidationError as e:
        raise DataValidation(
            f'Data does not match the provided schema. Validation errors: {e}'
        )
    except Exception as e:
        raise ComeCreateANewCase(
            f'{__name__}: unhandled error in validator: {e}'
        )
    return obj
