import logging
from pprint import pformat

from cerberus.validator import Validator

from .code_sql_types import code_types, sql_types

_logger = logging.getLogger(__name__)

parameter_types = [
    "boolean",
    "code",
    "connection",
    "date",
    "datetime",
    "enum_list",
    "enum",
    "int",
    "json",
    "metadata_table",
    "password",
    "shared_config",
    "sql",
    "string",
    "text",
    "time",
]
help_schema = {
    "oneof_schema": [
        {"header_id": {"type": "string", "required": False}},
        {"file": {"type": "string", "required": False}},
    ],
    "type": "dict",
}

parameter_field_schema = {
    "help": help_schema.copy(),
    "collapsed": {"required": False, "type": "boolean"},
    "many": {"required": False, "type": "boolean"},
    "required": {"required": False, "type": "boolean"},
    "direction": {"required": False, "type": "string"},
    "choices": {"dependencies": {"type": ["enum", "enum_list"]}, "type": "list"},
    "default_choices": {"dependencies": {"type": ["enum_list"]}, "type": "list"},
    "display_type": {"dependencies": {"type": ["enum_list"]}, "type": "string"},
    "connection_type_uuid": {"dependencies": {"type": ["connection"]}, "type": "string"},
    "shared_config_type_uuid": {
        "dependencies": {"type": ["shared_config"]},
        "type": "string",
    },
    "categories": {
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {"name": {"type": "string", "required": True}},
        },
    },
    "name": {"type": "string", "required": True},
    "dialect": {
        "type": "string",
        "oneof": [
            # If type is "sql", only check the list of sql types.
            # If type is "code", only check the list of language types (excluding sql).
            {"dependencies": {"type": ["sql"]}, "allowed": sql_types},
            {"dependencies": {"type": ["code"]}, "allowed": code_types},
        ],
    },
    "description": {"type": "string", "required": False},
    "display_name": {"type": "string", "required": True},
    "type": {
        "allowed": parameter_types,
        "required": True,
        "oneof": [
            # Bi-lateral dependencies
            # E.G. a field that is a "connection" type must have "connection_type_uuid" as a parameter.
            {"allowed": ["connection"], "dependencies": "connection_type_uuid"},
            {"allowed": ["shared_config"], "dependencies": "shared_config_type_uuid"},
            {"allowed": ["code", "sql"], "dependencies": "dialect"},
            {"allowed": ["enum", "enum_list"], "dependencies": "choices"},
            # Add above bi-lateral dependencies as "forbidden" so above dependencies are evaluated only once.
            {
                "forbidden": [
                    "connection",
                    "shared_config",
                    "code",
                    "sql",
                    "enum",
                    "enum_list",
                    "nested",
                ]
            },
        ],
    },
    "shared_field_type_uuid": {"type": "string", "required": False},
    "shared_object_type_uuid": {"type": "string", "required": False},
    "max": {"required": False, "type": "integer"},
    "min": {"required": False, "type": "integer"},
    "default": {"required": False},
    "show_on": {
        "type": "dict",
        "required": False,
        "schema": {
            "parameter_name": {"type": "string", "required": True},
            "parameter_value": {
                "type": "list",
                "schema": {
                    "type": ["string", "boolean", "number", "integer", "date", "datetime"]
                },
                "required": True,
            },
        },
    },
}

parameter_field_schema["parameters"] = {
    "dependencies": {"type": ["nested"]},
    "type": "list",
    "schema": {"type": "dict", "schema": parameter_field_schema.copy()},
}
parameter_field_schema["type"]["allowed"].append("nested")
parameter_field_schema["type"]["oneof"].insert(
    0,
    {"allowed": ["nested"], "dependencies": "parameters"},
)

parameter_group_schema = {
    "display_name": {"type": "string", "required": True},
    "collapsed": {"required": False, "type": "boolean"},
    "shared_parameter_group_uuid": {
        "required": False,
        "dependencies": {"type": ["group"]},
        "type": "string",
    },
    "description": {"type": "string", "required": False},
    "name": {"type": "string", "required": True},
    "type": {"allowed": ["group"], "required": True},
    "parameters": {
        "type": "list",
        "schema": {"type": "dict", "schema": parameter_field_schema.copy()},
    },
}

engine_schema = {
    "uuid": {
        "type": "string",
        "minlength": 8,
        "required": True,
        "regex": r"^[A-Z0-9]+([_-][A-Z0-9]+)*$",
    },
    "icons": {
        "type": "dict",
        "schema": {
            "1x": {"type": "string"},
            "2x": {"type": "string"},
            "3x": {"type": "string"},
        },
    },
    "help": help_schema.copy(),
    "alias": {"type": "string", "required": True},
    "description": {"type": "string", "required": True},
    "nnd_model_version": {"type": "integer", "required": True},
    "options": {"required": False, "type": "dict"},
    "categories": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {"name": {"type": "string", "required": True}},
        },
    },
    "parameter_categories": {
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {"name": {"type": "string", "required": True}},
        },
    },
    "type": {"allowed": ["engine"], "required": True},
    "actions": {
        "type": "dict",
        "required": True,
        "keyschema": {"type": "string"},
        "valueschema": {
            "type": "dict",
            "schema": {
                "description": {"type": "string", "required": True},
                "help": help_schema.copy(),
                "display_name": {"type": "string", "required": True},
                "parameters": {
                    "type": "list",
                    "required": True,
                    "schema": {"type": "dict", "schema": parameter_group_schema},
                },
            },
        },
    },
}


def _get_shared_type_schema(name):
    return {
        "uuid": {
            "type": "string",
            "minlength": 8,
            "required": True,
            "regex": r"^[A-Z0-9]+([_-][A-Z0-9]+)*$",
        },
        "alias": {"type": "string", "required": True},
        "description": {"type": "string", "required": True},
        "nnd_model_version": {"type": "integer", "required": True},
        "categories": {
            "type": "list",
            "required": True,
            "schema": {
                "type": "dict",
                "schema": {"name": {"type": "string", "required": True}},
            },
        },
        "type": {"allowed": [name], "required": True},
        "parameters": {
            "type": "list",
            "schema": {
                "type": "dict",
                "anyof_schema": [
                    parameter_field_schema.copy(),
                    parameter_group_schema.copy(),
                ],
            },
        },
    }


shared_config_type_schema = _get_shared_type_schema("shared_config_type")
shared_field_type_schema = _get_shared_type_schema("shared_field_type")
shared_object_type_schema = _get_shared_type_schema("shared_object_type")

connection_type_schema = {
    "uuid": {
        "type": "string",
        "minlength": 8,
        "required": True,
        "regex": r"^[A-Z0-9]+([_-][A-Z0-9]+)*$",
    },
    "alias": {"type": "string", "required": True},
    "description": {"type": "string", "required": True},
    "nnd_model_version": {"type": "integer", "required": True},
    "mask": {"type": "string", "required": False},
    "direction": {"required": False, "type": "string"},
    "categories": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {"name": {"type": "string", "required": True}},
        },
    },
    "type": {"allowed": ["connection"], "required": True},
    "parameters": {
        "type": "list",
        "schema": {"type": "dict", "schema": parameter_group_schema.copy()},
    },
}

schemas = {
    "engine": engine_schema,
    "shared_config_type": shared_config_type_schema,
    "shared_field_type": shared_field_type_schema,
    "shared_object_type": shared_object_type_schema,
    "connection": connection_type_schema,
}


def validate_model(model):
    schema = schemas[model["type"]]
    validator = Validator(schema)
    if not validator.validate(model):
        _logger.error(
            f"Errors validating {model['type']} model \n\t\t{pformat(validator.errors)}"
        )
        return False
    else:
        return True
