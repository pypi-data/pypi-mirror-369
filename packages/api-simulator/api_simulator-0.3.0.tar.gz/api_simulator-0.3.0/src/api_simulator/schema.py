from __future__ import annotations
from typing import Any, Dict
from jsonschema import Draft202012Validator

SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "rest": {
            "type": "object",
            "properties": {
                "port": {"type": "integer"},
                "path": {"type": "string"},
                "apis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {"type": "string"},
                            "path": {"type": "string"},
                            "status_code": {"type": "integer"},
                            "content_type": {"type": "string"},
                            "response": {},                   # JSON response body
                            "text": {"type": "string"},     # plain text body
                            "file": {"type": "string"},     # serve file from disk
                            "binary_b64": {"type": "string"}, # base64-encoded bytes
                            "range": {"type": "boolean"},   # enable HTTP Range for files/binary
                            "rules": {"type": "object"},    # conditional behavior
                            "stream": {                        # NDJSON or custom content streaming
                                "type": "object",
                                "properties": {
                                    "interval": {"type": ["number", "integer"]},
                                    "template": {},
                                    "count": {"type": ["integer", "null"]},
                                    "content_type": {"type": "string"}
                                },
                                "required": ["interval", "template"]
                            },
                            "sse": {                          # Server-Sent Events streaming
                                "type": "object",
                                "properties": {
                                    "interval": {"type": ["number", "integer"]},
                                    "template": {},
                                    "count": {"type": ["integer", "null"]},
                                    "event": {"type": "string"},
                                    "retry": {"type": ["integer", "null"]}
                                },
                                "required": ["interval", "template"]
                            }
                        },
                        "required": ["path"],
                        "anyOf": [
                            {"required": ["response"]},
                            {"required": ["text"]},
                            {"required": ["file"]},
                            {"required": ["binary_b64"]},
                            {"required": ["stream"]},
                            {"required": ["sse"]}
                        ],
                        "additionalProperties": True
                    }
                }
            },
            "required": ["port", "path", "apis"],
            "additionalProperties": True
        },
        "websocket": {
            "type": "object",
            "properties": {
                "port": {"type": "integer"},
                "path": {"type": "string"},
                "apis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "response": {},
                            "broadcast": {
                                "type": "object",
                                "properties": {
                                    "interval": {"type": ["number", "integer"]},
                                    "response": {},
                                    "rules": {"type": "object"}
                                },
                                "required": ["interval", "response"]
                            },
                            "rules": {"type": "object"},
                            "triggers": {"type": "object"}  # deprecated alias
                        },
                        "required": ["path"],
                        "additionalProperties": True
                    }
                }
            },
            "required": ["port", "path", "apis"]
        },
        "udp": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"},
                "apis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": ["string", "null"]},
                            "broadcast": {
                                "type": "object",
                                "properties": {
                                    "interval": {"type": ["number", "integer"]},
                                    "response": {}
                                },
                                "required": ["interval", "response"]
                            }
                        },
                        "required": ["broadcast"]
                    }
                }
            },
            "required": ["host", "port", "apis"]
        },
        "graphql": {
            "type": "object",
            "properties": {
                "port": {"type": ["integer", "null"]},
                "path": {"type": "string"},
                "subscriptions_path": {"type": "string"},
                "queries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "operationName": {"type": "string"},
                            "response": {},
                            "rules": {"type": "object"}
                        },
                        "required": ["operationName", "response"]
                    }
                },
                "mutations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "operationName": {"type": "string"},
                            "response": {},
                            "rules": {"type": "object"}
                        },
                        "required": ["operationName", "response"]
                    }
                },
                "subscriptions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "operationName": {"type": "string"},
                            "interval": {"type": ["number", "integer"]},
                            "response": {},
                            "rules": {"type": "object"}
                        },
                        "required": ["operationName", "interval", "response"]
                    }
                }
            },
            "required": ["path"],
            "additionalProperties": True
        }
    },
    "additionalProperties": False
}


def validate_config(config: Dict[str, Any]) -> None:
    Draft202012Validator(SCHEMA).validate(config)