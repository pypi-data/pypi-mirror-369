"""
End-to-end protocol tests with proper lifespan context
"""
import asyncio
import json
import os
import socket
import struct
import pytest
import msgpack
from fastapi.testclient import TestClient
from api_simulator.app import APISimulator


@pytest.mark.timeout(5)
def test_udp_broadcast_with_lifespan(monkeypatch):
    """Test UDP broadcast using lifespan context and loopback capture"""
    
    # Create UDP receiver on ephemeral port
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(("127.0.0.1", 0))
    recv_sock.settimeout(3.0)
    host, port = recv_sock.getsockname()
    
    # Override UDP target
    monkeypatch.setenv("APISIM_UDP_TARGET", f"{host}:{port}")
    
    config = {
        "udp": {
            "host": "127.0.0.1",
            "port": 5001,  # will be overridden
            "apis": [{
                "name": "test_broadcast",
                "broadcast": {
                    "interval": 0.1,
                    "response": {"type": "test", "seq": "{{ counter('udp_test') }}"}
                }
            }]
        }
    }
    
    sim = APISimulator(config)
    
    # Use TestClient to trigger lifespan
    with TestClient(sim.app) as client:
        # App is running with lifespan, UDP should be broadcasting
        
        try:
            # Receive first packet
            pkt, addr = recv_sock.recvfrom(65536)
            
            # Parse packet: magic(4) + timestamp(4) + length(2) + msgpack_body
            magic, ts, length = struct.unpack(">IIH", pkt[:10])
            body = pkt[10:]
            
            assert magic == 0xDEADBEEF
            assert len(body) == length
            
            payload = msgpack.unpackb(body, raw=False)
            assert payload["type"] == "test"
            assert "seq" in payload
            
            # Health check should show app is running
            resp = client.get("/health")
            assert resp.status_code == 200
            
        finally:
            recv_sock.close()
    
    # After context exit, lifespan should have cleaned up
    # (background tasks cancelled)


@pytest.mark.timeout(5) 
def test_websocket_with_lifespan():
    """Test WebSocket using asyncio with server task"""
    
    config = {
        "websocket": {
            "port": 9080,
            "path": "/ws",
            "apis": [{
                "path": "/test",
                "response": {"type": "pong"},
                "rules": {
                    "message.action == 'ping'": {
                        "response": {"type": "pong", "echo": "{{ message.action }}"}
                    }
                }
            }]
        }
    }
    
    sim = APISimulator(config)
    
    # Note: TestClient doesn't support WebSocket servers on different ports
    # We need to test WebSocket functionality differently
    # Using asyncio with the server task directly
    async def test_ws_async():
        # Start WebSocket server
        ws_task = asyncio.create_task(sim._ws_server(config["websocket"]))
        await asyncio.sleep(0.2)  # Let server start
        
        try:
            import websockets
            uri = "ws://localhost:9080/ws/test"
            async with websockets.connect(uri) as websocket:
                # Send ping
                await websocket.send(json.dumps({"action": "ping"}))
                
                # Receive pong
                response = await websocket.recv()
                data = json.loads(response)
                
                assert data["type"] == "pong"
                # Template may or may not be rendered depending on context
                assert "echo" in data or "message" in data
                
        finally:
            ws_task.cancel()
            try:
                await ws_task
            except asyncio.CancelledError:
                pass
    
    asyncio.run(test_ws_async())


@pytest.mark.timeout(5)
def test_graphql_subscription_websocket():
    """Test GraphQL subscriptions over WebSocket"""
    
    config = {
        "websocket": {
            "port": 9081,
            "path": "/ws",
            "apis": []
        },
        "graphql": {
            "subscriptions": [{
                "operationName": "TestSub",
                "interval": 0.1,
                "response": {"event": "test", "count": "{{ counter('gql_sub') }}"}
            }]
        }
    }
    
    sim = APISimulator(config)
    
    async def test_gql_async():
        ws_task = asyncio.create_task(sim._ws_server(config["websocket"]))
        await asyncio.sleep(0.2)
        
        try:
            import websockets
            uri = "ws://localhost:9081/ws/graphql"
            async with websockets.connect(uri) as websocket:
                # GraphQL transport-ws handshake
                await websocket.send(json.dumps({"type": "connection_init"}))
                ack = await websocket.recv()
                ack_data = json.loads(ack)
                assert ack_data["type"] == "connection_ack"
                
                # Subscribe
                await websocket.send(json.dumps({
                    "id": "1",
                    "type": "subscribe",
                    "payload": {"operationName": "TestSub"}
                }))
                
                # Receive at least one subscription update
                msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(msg)
                assert data["type"] == "next"
                assert data["id"] == "1"
                assert "event" in data["payload"]["data"]
                assert "count" in data["payload"]["data"]
                
        finally:
            ws_task.cancel()
            try:
                await ws_task
            except asyncio.CancelledError:
                pass
    
    asyncio.run(test_gql_async())


def test_health_during_lifespan():
    """Test health endpoint reports correct metrics during lifespan"""
    
    config = {
        "rest": {
            "port": 8000,
            "path": "/api",
            "apis": []
        }
    }
    
    sim = APISimulator(config)
    
    with TestClient(sim.app) as client:
        # Check health endpoint
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert "metrics" in data
        assert data["metrics"]["ws_clients"] == 0