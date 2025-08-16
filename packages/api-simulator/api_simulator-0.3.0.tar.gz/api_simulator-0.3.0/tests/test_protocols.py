"""
Comprehensive protocol tests for api-simulator v0.3.0
Tests REST, WebSocket, GraphQL, UDP, OpenAPI export, and SSE streaming.
"""
import asyncio
import json
import socket
import struct
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest
import msgpack
import websockets
from fastapi.testclient import TestClient

from api_simulator.app import APISimulator


@pytest.fixture
def full_config():
    """Complete configuration covering all protocols"""
    return {
        "rest": {
            "port": 8000,
            "path": "/api/v1",
            "apis": [
                {
                    "method": "GET",
                    "path": "/users/{user_id}",
                    "response": {"id": "{{ path('user_id') }}", "name": "Test User"},
                    "status_code": 200
                },
                {
                    "method": "POST", 
                    "path": "/orders",
                    "response": {"order_id": "{{ counter('orders') }}", "status": "created"},
                    "rules": {
                        "body.amount == 2000": {
                            "status": 402,
                            "response": {"error": "payment_required"}
                        }
                    }
                },
                {
                    "method": "GET",
                    "path": "/stream/events",
                    "sse": {
                        "interval": 0.1,
                        "template": {"event": "ping", "ts": "{{ unix_timestamp() }}"},
                        "count": 3,
                        "event": "heartbeat"
                    }
                },
                {
                    "method": "GET", 
                    "path": "/stream/data",
                    "stream": {
                        "interval": 0.1,
                        "template": {"line": "{{ counter('lines') }}"},
                        "count": 2
                    }
                }
            ]
        },
        "websocket": {
            "port": 9080,
            "path": "/ws",
            "apis": [
                {
                    "path": "/events",
                    "response": {"type": "pong", "ts": "{{ unix_timestamp() }}"},
                    "rules": {
                        "message.action == 'ping'": {
                            "response": {"type": "pong", "received": "{{ message.action }}"}
                        }
                    }
                },
                {
                    "path": "/broadcast", 
                    "broadcast": {
                        "interval": 0.2,
                        "response": {"broadcast": "{{ counter('broadcasts') }}"}
                    }
                }
            ]
        },
        "graphql": {
            "port": 8000,
            "path": "/graphql",
            "queries": [
                {
                    "operationName": "GetUser",
                    "response": {"user": {"id": "123", "name": "GraphQL User"}}
                }
            ],
            "mutations": [
                {
                    "operationName": "CreateUser", 
                    "response": {"user": {"id": "{{ counter('gql_users') }}", "created": True}}
                }
            ],
            "subscriptions": [
                {
                    "operationName": "UserUpdates",
                    "interval": 0.1,
                    "response": {"user": {"id": "123", "updated": "{{ unix_timestamp() }}"}}
                }
            ]
        },
        "udp": {
            "host": "127.0.0.1",
            "port": 5001,
            "apis": [
                {
                    "name": "heartbeat",
                    "broadcast": {
                        "interval": 0.1,
                        "response": {"type": "heartbeat", "seq": "{{ counter('udp_seq') }}"}
                    }
                }
            ]
        }
    }


class TestRESTProtocol:
    """Test REST API functionality"""
    
    def test_basic_rest_response(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        # Test path parameter templating
        resp = client.get("/api/v1/users/42")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "42"
        assert data["name"] == "Test User"
    
    def test_rest_rules_trigger(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        # Normal order
        resp = client.post("/api/v1/orders", json={"amount": 100})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "created"
        
        # High amount triggers rule
        resp = client.post("/api/v1/orders", json={"amount": 2000})
        assert resp.status_code == 402
        data = resp.json()
        assert data["error"] == "payment_required"
    
    def test_sse_streaming(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        with client.stream("GET", "/api/v1/stream/events") as resp:
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")
            
            # Read first few events
            events = []
            for line in resp.iter_lines():
                if line.startswith("event:"):
                    assert "heartbeat" in line
                elif line.startswith("data:"):
                    event_data = json.loads(line[5:].strip())
                    events.append(event_data)
                    if len(events) >= 2:
                        break
            
            assert len(events) >= 2
            assert all("ts" in event for event in events)
    
    def test_ndjson_streaming(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        with client.stream("GET", "/api/v1/stream/data") as resp:
            assert resp.status_code == 200
            assert "application/x-ndjson" in resp.headers.get("content-type", "")
            
            lines = []
            for line in resp.iter_lines():
                if line.strip():
                    data = json.loads(line)
                    lines.append(data)
                    if len(lines) >= 2:
                        break
            
            assert len(lines) == 2
            # Counter starts at 0, so first values are 0 and 1
            assert lines[0]["line"] == "0"
            assert lines[1]["line"] == "1"


class TestGraphQLProtocol:
    """Test GraphQL functionality"""
    
    def test_graphql_query(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        query_body = {
            "operationName": "GetUser",
            "query": "query GetUser { user { id name } }"
        }
        
        resp = client.post("/graphql", json=query_body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["user"]["id"] == "123"
        assert data["data"]["user"]["name"] == "GraphQL User"
    
    def test_graphql_mutation(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        mutation_body = {
            "operationName": "CreateUser",
            "query": "mutation CreateUser { user { id created } }"
        }
        
        resp = client.post("/graphql", json=mutation_body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["user"]["created"] is True
        assert data["data"]["user"]["id"] == "0"  # Counter starts at 0
    
    def test_graphql_unknown_operation(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        body = {"operationName": "UnknownOp"}
        resp = client.post("/graphql", json=body)
        assert resp.status_code == 400
        data = resp.json()
        assert "not found" in data["errors"][0]["message"]


@pytest.mark.skip(reason="Replaced by E2E tests in test_e2e_protocols.py")
@pytest.mark.asyncio
class TestWebSocketProtocol:
    """Test WebSocket functionality"""
    
    async def test_websocket_basic_response(self, full_config):
        sim = APISimulator(full_config)
        
        # Start WebSocket server task
        ws_task = asyncio.create_task(sim._ws_server(full_config["websocket"]))
        await asyncio.sleep(0.1)  # Let server start
        
        try:
            uri = "ws://localhost:9080/ws/events"
            async with websockets.connect(uri) as websocket:
                # Send ping message
                await websocket.send(json.dumps({"action": "ping"}))
                
                # Receive pong response
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(response)
                
                assert data["type"] == "pong"
                assert data["received"] == "ping"
        finally:
            ws_task.cancel()
            try:
                await ws_task
            except asyncio.CancelledError:
                pass
    
    async def test_websocket_broadcast(self, full_config):
        sim = APISimulator(full_config)
        
        ws_task = asyncio.create_task(sim._ws_server(full_config["websocket"]))
        await asyncio.sleep(0.1)
        
        try:
            uri = "ws://localhost:9080/ws/broadcast"
            async with websockets.connect(uri) as websocket:
                # Wait for broadcast messages
                messages = []
                for _ in range(3):
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(msg)
                        messages.append(data)
                    except asyncio.TimeoutError:
                        break
                
                assert len(messages) >= 2
                assert all("broadcast" in msg for msg in messages)
                # Counter should increment
                assert int(messages[1]["broadcast"]) > int(messages[0]["broadcast"])
        finally:
            ws_task.cancel()
            try:
                await ws_task
            except asyncio.CancelledError:
                pass
    
    async def test_graphql_subscriptions(self, full_config):
        sim = APISimulator(full_config)
        
        ws_task = asyncio.create_task(sim._ws_server(full_config["websocket"]))
        await asyncio.sleep(0.1)
        
        try:
            # GraphQL subscriptions should be at /ws/graphql by default
            uri = "ws://localhost:9080/ws/graphql"
            async with websockets.connect(uri) as websocket:
                # GraphQL transport-ws handshake
                await websocket.send(json.dumps({"type": "connection_init"}))
                ack = await websocket.recv()
                ack_data = json.loads(ack)
                assert ack_data["type"] == "connection_ack"
                
                # Subscribe to UserUpdates
                await websocket.send(json.dumps({
                    "id": "1",
                    "type": "subscribe", 
                    "payload": {"operationName": "UserUpdates"}
                }))
                
                # Receive subscription data
                messages = []
                for _ in range(2):
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(msg)
                        if data.get("type") == "next":
                            messages.append(data)
                    except asyncio.TimeoutError:
                        break
                
                assert len(messages) >= 1
                assert messages[0]["id"] == "1"
                assert messages[0]["type"] == "next"
                assert "user" in messages[0]["payload"]["data"]
        finally:
            ws_task.cancel()
            try:
                await ws_task
            except asyncio.CancelledError:
                pass


class TestUDPProtocol:
    """Test UDP functionality"""
    
    def test_udp_config_validation(self, full_config):
        """Test that UDP configuration is parsed correctly"""
        sim = APISimulator(full_config)
        
        # Verify UDP config is loaded
        udp_config = full_config["udp"]
        assert udp_config["host"] == "127.0.0.1"
        assert udp_config["port"] == 5001
        assert len(udp_config["apis"]) == 1
        assert udp_config["apis"][0]["name"] == "heartbeat"
        
        # Basic smoke test - instantiation should work
        from api_simulator.app import UdpApiConfig
        api = UdpApiConfig(**udp_config["apis"][0])
        assert api.name == "heartbeat"
        assert api.broadcast.interval == 0.1


class TestOpenAPIExport:
    """Test OpenAPI export functionality"""
    
    def test_openapi_export_basic(self, full_config):
        from api_simulator.openapi import build_openapi
        
        spec = build_openapi(full_config)
        
        assert spec["openapi"] == "3.0.3"
        assert spec["info"]["title"] == "API Simulator"
        assert spec["info"]["version"] == "0.3.0"
        assert "paths" in spec
        
        # Check REST endpoints are included
        paths = spec["paths"]
        assert "/api/v1/users/{user_id}" in paths
        assert "/api/v1/orders" in paths
        
        # Check GET user endpoint
        user_path = paths["/api/v1/users/{user_id}"]
        assert "get" in user_path
        assert user_path["get"]["responses"]["200"]["content"]["application/json"]
        
        # Check POST orders endpoint  
        orders_path = paths["/api/v1/orders"]
        assert "post" in orders_path
        assert orders_path["post"]["responses"]["200"]["content"]["application/json"]
        
        # Check streaming endpoints
        assert "/api/v1/stream/events" in paths
        sse_path = paths["/api/v1/stream/events"]
        assert sse_path["get"]["responses"]["200"]["content"]["text/event-stream"]
        
        assert "/api/v1/stream/data" in paths
        stream_path = paths["/api/v1/stream/data"]
        assert stream_path["get"]["responses"]["200"]["content"]["application/x-ndjson"]
    
    def test_openapi_with_graphql(self, full_config):
        from api_simulator.openapi import build_openapi
        
        spec = build_openapi(full_config)
        
        # GraphQL should appear as single POST endpoint
        assert "/graphql" in spec["paths"]
        gql_path = spec["paths"]["/graphql"]
        assert "post" in gql_path
        assert gql_path["post"]["responses"]["200"]["content"]["application/json"]
    
    def test_openapi_extensions(self, full_config):
        from api_simulator.openapi import build_openapi
        
        spec = build_openapi(full_config, include_extensions=True)
        
        # Should include x-simulator extensions
        assert "x-simulator" in spec
        extensions = spec["x-simulator"]
        
        assert "websocket" in extensions
        assert "udp" in extensions
        
        # WebSocket info (it's a list of endpoints)
        ws_endpoints = extensions["websocket"]
        assert isinstance(ws_endpoints, list)
        assert len(ws_endpoints) == 2
        assert any(ep["path"] == "/ws/events" for ep in ws_endpoints)
        assert any(ep["path"] == "/ws/broadcast" for ep in ws_endpoints)
        
        # UDP info
        udp_info = extensions["udp"]
        assert udp_info["host"] == "127.0.0.1"
        assert udp_info["port"] == 5001


class TestHealthEndpoint:
    """Test health endpoint functionality"""
    
    def test_health_endpoint(self, full_config):
        sim = APISimulator(full_config)
        client = TestClient(sim.app)
        
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["ok"] is True
        assert "metrics" in data
        assert "ws_clients" in data["metrics"]
        assert data["metrics"]["ws_clients"] == 0  # No active connections


if __name__ == "__main__":
    pytest.main([__file__, "-v"])