from __future__ import annotations
from typing import Any, Dict, Optional
import copy
import json

def _content_for_rest_api(api: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a single REST item to OpenAPI 'content' with a conservative schema + example.
    """
    ct = api.get("content_type") or (
        "application/json" if api.get("response") is not None else
        "text/plain" if api.get("text") is not None else
        "application/octet-stream"
    )
    if api.get("file"):
        schema = {"type": "string", "format": "binary"}
        example = None
    elif api.get("binary_b64"):
        schema = {"type": "string", "format": "byte"}
        example = None
    elif api.get("text") is not None:
        schema = {"type": "string"}
        example = api.get("text")
    elif api.get("stream"):
        # NDJSON — represent as newline-delimited JSON strings
        ct = api["stream"].get("content_type") or "application/x-ndjson"
        schema = {"type": "string", "description": "NDJSON stream (one JSON object per line)"}
        # Use literal example without escaping for better display
        example = {"tick":1,"ts":1700000000}
    elif api.get("sse"):
        ct = "text/event-stream"
        schema = {"type": "string", "description": "SSE event stream (event: name\\ndata: <json>\\n\\n)"}
        example = {"symbol":"ACME","price":12.34}
    else:
        # JSON response (templated) — we can't know the exact schema; show as 'object'
        schema = {"type": "object"}
        example = api.get("response")
    return {
        ct: {
            "schema": schema,
            **({"example": example} if example is not None else {})
        }
    }

def build_openapi(config: Dict[str, Any], *, title="API Simulator", version="0.3.0",
                  server_url: Optional[str] = None, include_extensions: bool = True) -> Dict[str, Any]:
    """
    Build a minimal-but-useful OpenAPI 3.0 spec from the simulator config.
    - REST: all endpoints with method, status and content.
    - GraphQL: one POST /graphql with simple body schema; optional note about subscriptions.
    - WebSocket/UDP: exposed under x-simulator extensions (non-standard, for visibility).
    """
    openapi: Dict[str, Any] = {
        "openapi": "3.0.3",
        "info": {"title": title, "version": version},
        "paths": {},
    }
    if server_url:
        openapi["servers"] = [{"url": server_url}]

    rest = (config.get("rest") or {})
    prefix = rest.get("path", "")
    for item in rest.get("apis", []):
        method = (item.get("method") or "GET").lower()
        path = f"{prefix}{item['path']}"
        status = int(item.get("status_code") or 200)
        content = _content_for_rest_api(item)
        path_item = openapi["paths"].setdefault(path, {})
        # Add description for streaming endpoints
        description = None
        if item.get("stream"):
            description = "⚠️ Streaming endpoint - sends continuous NDJSON data. Use curl or browser tools, not Swagger UI."
        elif item.get("sse"):
            description = "⚠️ Server-Sent Events - sends continuous SSE stream. Use curl or EventSource API, not Swagger UI."
            
        op = {
            "summary": f"{method.upper()} {path}",
            **({"description": description} if description else {}),
            "responses": {
                str(status): {
                    "description": "OK",
                    "content": content
                }
            }
        }
        # streaming endpoints often return 200; rules may emit 204/302/429 etc.
        # we add a minimal default entry to hint that other statuses may occur
        op["responses"].setdefault("default", {"description": "Possible alternate status via rules"})
        path_item[method] = op

    gql = (config.get("graphql") or {})
    if gql:
        p = gql.get("path", "/graphql")
        openapi["paths"].setdefault(p, {})
        # Collect available operations for better documentation
        operations = []
        for q in gql.get("queries", []):
            operations.append(q.get("operationName"))
        for m in gql.get("mutations", []):
            operations.append(m.get("operationName"))
        
        example_op = operations[0] if operations else "YourOperationName"
        
        openapi["paths"][p]["post"] = {
            "summary": "GraphQL endpoint (operationName-only)",
            "description": f"Available operations: {', '.join(operations)}" if operations else "No operations configured",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"operationName": {"type": "string", "enum": operations if operations else None}},
                            "required": ["operationName"]
                        },
                        "example": {"operationName": example_op}
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "GraphQL response envelope",
                    "content": {"application/json": {"schema": {"type": "object"}}}
                },
                "400": {
                    "description": "Operation not found",
                    "content": {"application/json": {"schema": {"type": "object"}}}
                }
            }
        }

    if include_extensions:
        ext: Dict[str, Any] = {}
        ws = (config.get("websocket") or {})
        if ws:
            ws_prefix = ws.get("path", "")
            ext["websocket"] = [{
                "path": ws_prefix + api.get("path",""),
                "broadcast": bool(api.get("broadcast")),
                "rules": bool(api.get("rules") or api.get("triggers")),
            } for api in ws.get("apis", [])]
        udp = (config.get("udp") or {})
        if udp:
            ext["udp"] = {
                "host": udp.get("host"),
                "port": udp.get("port"),
                "streams": [{"name": api.get("name")} for api in udp.get("apis", [])]
            }
        if ext:
            openapi["x-simulator"] = ext

    return openapi