from __future__ import annotations
import asyncio
import base64
import json
import logging
import mimetypes
import socket
import ssl
import struct
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Set

import msgpack
import websockets
from fastapi import FastAPI, Response, Request
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from .templates import TemplateEngine

logger = logging.getLogger("api_simulator")

# --------- Pydantic config models (lightweight) ---------
class RestApiConfig(BaseModel):
    method: str = "GET"
    path: str
    status_code: int = 200
    # body variants
    response: Optional[Dict[str, Any]] = None  # JSON
    text: Optional[str] = None
    file: Optional[str] = None
    binary_b64: Optional[str] = None
    content_type: Optional[str] = None
    # enable HTTP Range on file/binary endpoints
    range: bool = True
    # behavior
    rules: Optional[Dict[str, Any]] = None
    stream: Optional[Dict[str, Any]] = None  # {interval, template, count?, content_type?}
    sse: Optional[Dict[str, Any]] = None     # {interval, template, count?, event?, retry?}

class WebSocketBroadcastConfig(BaseModel):
    interval: float
    response: Dict[str, Any]
    rules: Optional[Dict[str, Any]] = None  # unified rules for broadcasts

class WebSocketApiConfig(BaseModel):
    path: str
    response: Optional[Dict[str, Any]] = None
    broadcast: Optional[WebSocketBroadcastConfig] = None
    # unified name
    rules: Optional[Dict[str, Any]] = None
    # deprecated alias (still accepted)
    triggers: Optional[Dict[str, Any]] = None

class UdpBroadcastDetails(BaseModel):
    interval: float
    response: Dict[str, Any]

class UdpApiConfig(BaseModel):
    name: Optional[str] = None
    broadcast: UdpBroadcastDetails

class SimulatorConfig(BaseModel):
    rest: Optional[Dict[str, Any]] = None
    websocket: Optional[Dict[str, Any]] = None
    udp: Optional[Dict[str, Any]] = None
    graphql: Optional[Dict[str, Any]] = None

# ---------------- Trigger & actions ----------------
class ActionExecutor:
    def __init__(self) -> None:
        self.blocked: Dict[str, float] = {}
        self.deprecation_logged = False
        
    def is_blocked(self, cid: str) -> bool:
        until = self.blocked.get(cid)
        if not until:
            return False
        if time.time() < until:
            return True
        self.blocked.pop(cid, None)
        return False
        
    async def apply(self, actions: Dict[str, Any], websocket=None) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        if "delay" in actions:
            d = actions["delay"]
            try:
                sec = float(str(d).rstrip("s"))
            except Exception:
                sec = 0.0
            await asyncio.sleep(sec)
            res["delayed"] = sec
        if "block" in actions and websocket is not None:
            b = float(str(actions["block"]).rstrip("s"))
            self.blocked[str(id(websocket))] = time.time() + b
            res["blocked"] = b
        if "restart" in actions and websocket is not None:
            await websocket.close(code=1012, reason="Server restart by trigger")
            res["restarted"] = True
        if actions.get("ignore"):
            res["ignored"] = True
        # WebSocket transport-level close
        if "close" in actions and websocket is not None:
            c = actions["close"]
            code = int((c or {}).get("code", 1000))
            reason = (c or {}).get("reason", "Closed by rule")
            await websocket.close(code=code, reason=reason)
            res["closed"] = True
        return res

class TriggerProcessor:
    def __init__(self, engine: TemplateEngine, actions: ActionExecutor) -> None:
        self.engine = engine
        self.actions = actions
        
    def _eval_cond(self, cond: str, ctx: Dict[str, Any]) -> bool:
        # probability [0,1]
        try:
            p = float(cond)
            if 0 <= p <= 1:
                return self.engine.random.random() < p
        except ValueError:
            pass
        # elapsed seconds since connect (for WS); for REST this just evaluates false unless client_state provided
        try:
            secs = float(cond)
            ct = ctx.get("client_state", {}).get("connect_time", time.time())
            return (time.time() - ct) >= secs
        except ValueError:
            pass
        # dotted equality: query.foo == "x", path.user_id == "123", header.X == "y", body.key == "z"
        if "==" in cond:
            left, right = [s.strip() for s in cond.split("==", 1)]
            right = right.strip('\"\'')
            obj: Any = ctx
            for part in left.split('.'):
                if isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    return False
            return str(obj) == right
        return False
        
    def _apply_field_updates(self, base: Optional[Dict[str, Any]], updates: List[Dict[str, Any]]):
        out: Dict[str, Any] = dict(base or {})
        for upd in updates:
            for path, value in upd.items():
                cur = out
                parts = path.split('.')
                for p in parts[:-1]:
                    cur = cur.setdefault(p, {})  # type: ignore
                cur[parts[-1]] = self.engine.render(value)
        return out
        
    async def process(self, rules: Optional[Dict[str, Any]], ctx: Dict[str, Any], initial: Optional[Dict[str, Any]], websocket=None):
        resp = dict(initial) if initial else None
        should_send = True
        meta: Dict[str, Any] = {}  # status/headers/redirect
        for cond, acts in (rules or {}).items():
            if self._eval_cond(cond, ctx):
                if "fields" in acts:
                    resp = self._apply_field_updates(resp, acts["fields"])  # type: ignore
                if "response" in acts:
                    resp = self.engine.render(acts["response"])  # type: ignore
                # collect transport metadata
                if "status" in acts:
                    try: meta["status"] = int(acts["status"])
                    except Exception: pass
                if "headers" in acts and isinstance(acts["headers"], dict):
                    meta.setdefault("headers", {}).update(self.engine.render(acts["headers"]))  # type: ignore
                if "redirect" in acts and isinstance(acts["redirect"], dict):
                    meta["redirect"] = self.engine.render(acts["redirect"])  # type: ignore
                action_result = await self.actions.apply(acts, websocket)
                if action_result.get("ignored") or action_result.get("restarted") or action_result.get("closed"):
                    should_send = False
        return resp, should_send, meta

# ---------------- Main simulator ----------------
class APISimulator:
    def __init__(self, config: Dict[str, Any], engine: Optional[TemplateEngine] = None) -> None:
        self.config_raw = config
        self.cfg = SimulatorConfig(**config)
        self.engine = engine or TemplateEngine()
        self.actions = ActionExecutor()
        self.triggers = TriggerProcessor(self.engine, self.actions)

        self.ws_clients: Dict[str, Set] = {}
        self.client_states: Dict[str, Dict[str, Any]] = {}
        self.ws_path_cfg: Dict[str, Dict[str, Any]] = {}
        
        # GraphQL subscriptions registry
        gql_cfg = (config.get("graphql") or {})
        self.gql_subscriptions = {s["operationName"]: s for s in gql_cfg.get("subscriptions", [])}
        self.gql_sub_path = (gql_cfg.get("subscriptions_path")  # explicit override
                             or ((config.get("websocket") or {}).get("path","") + "/graphql") if config.get("websocket") else "/graphql")

        self.app = FastAPI(lifespan=self._lifespan)
        # Browsers disallow "*" with credentials; default to credentials=False for safety
        # Allow common development origins including Swagger UI
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=False,
        )
        self._routes_rest()
        self._routes_graphql()
        self._routes_health()

        self.ssl_context: Optional[ssl.SSLContext] = None  # for WS when running with WSS

        # Optional: prefer our enriched OpenAPI if module is available
        try:
            from .openapi import build_openapi
            def _custom_openapi():
                # Use relative server for proxy-friendly behavior
                return build_openapi(self.config_raw, server_url=None)
            self.app.openapi = _custom_openapi  # type: ignore[assignment]
        except Exception:
            pass

    # ------------ REST ------------
    def _routes_rest(self) -> None:
        rest = self.cfg.rest
        if not rest: return
        prefix = rest.get("path", "")
        for api in rest.get("apis", []):
            api_obj = RestApiConfig(**api)
            full = f"{prefix}{api_obj.path}"

            async def handler(request: Request, _api=api_obj):
                # Build request context for templating & rules
                try:
                    body_json = await request.json()
                except Exception:
                    body_json = None
                ctx = {
                    "headers": dict(request.headers),
                    "query": dict(request.query_params),
                    "path": request.path_params,
                    "method": request.method,
                    "body": body_json,
                }

                with self.engine.use(ctx):
                    # SSE (first) or NDJSON stream (rules apply before streaming begins)
                    if _api.sse:
                        sse = _api.sse
                        interval = float(sse.get("interval", 1.0))
                        template = sse.get("template", {})
                        count = sse.get("count")
                        event = sse.get("event")
                        retry = sse.get("retry")
                        status = 200
                        headers = {}

                        # Apply rules once to seed headers/status and optionally override template
                        if _api.rules:
                            base_template = template
                            resp, should_send, meta = await self.triggers.process(_api.rules, ctx, base_template, websocket=None)
                            if not should_send:
                                return Response(status_code=204)
                            if resp is not None:
                                template = resp
                            status = int(meta.get("status", 200))
                            headers = meta.get("headers") or {}

                        async def agen():
                            # optional retry advisory
                            if retry:
                                yield f"retry: {int(retry)}\n\n".encode()
                            n = 0
                            while True:
                                payload = self.engine.render(template)
                                lines = []
                                if event: lines.append(f"event: {event}")
                                lines.append("data: " + json.dumps(payload))
                                yield ("\n".join(lines) + "\n\n").encode()
                                n += 1
                                if count is not None and n >= int(count):
                                    break
                                await asyncio.sleep(interval)

                        return StreamingResponse(agen(), media_type="text/event-stream", status_code=status, headers=headers)

                    if _api.stream:
                        interval = float(_api.stream.get("interval", 1.0))
                        template = _api.stream.get("template", {})
                        count = _api.stream.get("count")  # None -> infinite
                        ct = _api.stream.get("content_type") or "application/x-ndjson"
                        status = 200
                        headers = {}

                        # Apply rules once to seed headers/status and optionally override template
                        if _api.rules:
                            base_template = template
                            resp, should_send, meta = await self.triggers.process(_api.rules, ctx, base_template, websocket=None)
                            if not should_send:
                                return Response(status_code=204)
                            if resp is not None:
                                template = resp
                            status = int(meta.get("status", 200))
                            headers = meta.get("headers") or {}

                        async def agen():
                            n = 0
                            while True:
                                payload = self.engine.render(template)
                                if ct == "application/x-ndjson":
                                    chunk = json.dumps(payload) + "\n"
                                    yield chunk.encode()
                                else:
                                    if isinstance(payload, (dict, list)):
                                        yield json.dumps(payload).encode()
                                    elif isinstance(payload, str):
                                        yield payload.encode()
                                    else:
                                        yield payload
                                n += 1
                                if count is not None and n >= int(count):
                                    break
                                await asyncio.sleep(interval)

                        return StreamingResponse(agen(), media_type=ct, status_code=status, headers=headers)

                    status = _api.status_code
                    # Determine base body variant
                    is_binary_like = False  # Initialize for all paths
                    if _api.response is not None:
                        body = self.engine.render(_api.response)
                        media = _api.content_type or "application/json"
                        raw = json.dumps(body).encode()
                    elif _api.text is not None:
                        body = self.engine.render(_api.text)
                        media = _api.content_type or "text/plain"
                        raw = (body if isinstance(body, str) else str(body)).encode()
                    elif _api.file is not None:
                        media = _api.content_type or (mimetypes.guess_type(_api.file)[0] or "application/octet-stream")
                        with open(_api.file, "rb") as f:
                            raw = f.read()
                        is_binary_like = True
                    elif _api.binary_b64 is not None:
                        media = _api.content_type or "application/octet-stream"
                        raw = base64.b64decode(_api.binary_b64)
                        is_binary_like = True
                    else:
                        body = {}
                        media = "application/json"
                        raw = b"{}"

                    # Apply rules (same syntax as WS triggers) against request context
                    if _api.rules:
                        initial_json = None
                        if media == "application/json":
                            try:
                                initial_json = json.loads(raw)
                            except Exception:
                                initial_json = None
                        resp, should_send, meta = await self.triggers.process(_api.rules, ctx, initial_json, websocket=None)
                        if not should_send:
                            return Response(status_code=204)
                        if resp is not None:
                            raw = json.dumps(resp).encode()
                            media = "application/json"
                        # apply transport meta
                        if meta.get("redirect"):
                            redir = meta["redirect"] or {}
                            loc = redir.get("location")
                            sc = int(redir.get("status", 302))
                            hdrs = {"Location": loc} if loc else {}
                            if meta.get("headers"): hdrs.update(meta["headers"])
                            return Response(status_code=sc, headers=hdrs)
                        if meta.get("status"):
                            status = int(meta["status"])

                    # HTTP Range for binary/file bodies (after rules/redirect handling)
                    headers_out = (meta.get("headers") or {}) if _api.rules else {}
                    if is_binary_like:
                        headers_out["Accept-Ranges"] = "bytes"
                    if is_binary_like and _api.range:
                        rng = request.headers.get("Range")
                        if rng:
                            start, end, total, chunk = self._apply_range(rng, raw)
                            headers_out["Content-Range"] = f"bytes {start}-{end}/{total}"
                            return Response(content=chunk, media_type=media, status_code=206, headers=headers_out)

                    # HEAD requests for binary/file: send headers only
                    if request.method == "HEAD":
                        return Response(status_code=status, media_type=media, headers=headers_out)

                    return Response(content=raw, media_type=media, status_code=status, headers=headers_out)

            # Add HEAD method for file/binary endpoints
            methods = [api_obj.method]
            if api_obj.file or api_obj.binary_b64:
                methods.append("HEAD")
            self.app.add_api_route(full, handler, methods=methods, status_code=api_obj.status_code)
            logger.info("REST %s %s -> %s", api_obj.method, full, api_obj.status_code)

    # helper: parse single Range "bytes=start-end"
    def _parse_range(self, header: str, total: int):
        try:
            unit, spec = header.split("=")
            if unit.strip() != "bytes":
                return 0, total - 1
            start_s, end_s = spec.split("-")
            start = int(start_s) if start_s else 0
            end = int(end_s) if end_s else total - 1
            start = max(0, min(start, total - 1))
            end = max(start, min(end, total - 1))
            return start, end
        except Exception:
            return 0, total - 1

    def _apply_range(self, header: str, raw: bytes):
        total = len(raw)
        start, end = self._parse_range(header, total)
        return start, end, total, raw[start:end+1]

    # --------- GraphQL (simple by operationName) ---------
    def _routes_graphql(self) -> None:
        gql = self.config_raw.get("graphql")
        if not gql: return
        path = gql.get("path", "/graphql")
        # capture responses and optional rules
        queries = {q["operationName"]: q for q in gql.get("queries", [])}
        mutations = {m["operationName"]: m for m in gql.get("mutations", [])}
        
        async def handler(request: Request):
            try:
                body = await request.json()
            except Exception:
                body = {}
            
            ctx = {
                "headers": dict(request.headers),
                "query": dict(request.query_params),
                "path": request.path_params,
                "method": request.method,
                "body": body,
            }
            with self.engine.use(ctx):
                operation_name = body.get("operationName") if body else None
                if not operation_name:
                    return Response(content=json.dumps({"errors":[{"message":"Operation name missing"}]}), status_code=400)
                entry = queries.get(operation_name) or mutations.get(operation_name)
                if entry is None:
                    return Response(content=json.dumps({"errors":[{"message":f"Operation '{operation_name}' not found"}]}), status_code=400)
                base = self.engine.render(entry.get("response"))
                rules = entry.get("rules")
                meta: Dict[str, Any] = {}
                if rules:
                    base, should_send, meta = await self.triggers.process(rules, ctx, base, websocket=None)
                    if not should_send:
                        return Response(status_code=204)
                status = int(meta.get("status", 200))
                headers = meta.get("headers") or {}
                # GraphQL commonly returns 200 even on errors; we allow transport status overrides.
                return Response(content=json.dumps({"data": base}), media_type="application/json", status_code=status, headers=headers)
                
        self.app.add_api_route(path, handler, methods=["POST"])        
        logger.info("GraphQL POST %s", path)

    # ------------- health -------------
    def _routes_health(self) -> None:
        @self.app.get("/health")
        def health():
            return {
                "ok": True,
                "metrics": {
                    "ws_clients": sum(len(v) for v in self.ws_clients.values()),
                }
            }


    # ---------- lifespan (background WS + UDP) ----------
    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        tasks: List[asyncio.Task] = []
        ws_cfg = self.cfg.websocket
        if ws_cfg:
            tasks.append(asyncio.create_task(self._ws_server(ws_cfg)))
        elif self.gql_subscriptions:
            logger.info("GraphQL subscriptions configured but WebSocket server is disabled")
        udp_cfg = self.cfg.udp
        if udp_cfg:
            for api in udp_cfg.get("apis", []):
                tasks.append(asyncio.create_task(self._udp_loop(api, udp_cfg["host"], udp_cfg["port"])))
        try:
            yield
        finally:
            for t in tasks:
                t.cancel()
            await asyncio.sleep(0.05)

    # ----------------- WebSockets -----------------
    async def _ws_server(self, ws_cfg: Dict[str, Any]):
        port = int(ws_cfg.get("port"))
        prefix = ws_cfg.get("path", "")
        self.ws_path_cfg = {f"{prefix}{api['path']}": api for api in ws_cfg.get("apis", [])}
        
        async def router(websocket):
            path = websocket.request.path
            # GraphQL subscriptions route
            if path == self.gql_sub_path and self.gql_subscriptions:
                await self._ws_graphql(websocket)
            else:
                await self._ws_client(websocket, path)
                
        server = await websockets.serve(router, "0.0.0.0", port, ssl=self.ssl_context)
        logger.info("WebSocket on %s://0.0.0.0:%d%s (prefix)", "wss" if self.ssl_context else "ws", port, prefix)
        if self.gql_subscriptions:
            logger.info("GraphQL subscriptions at %s://0.0.0.0:%d%s", "wss" if self.ssl_context else "ws", port, self.gql_sub_path)
        
        # Broadcast tasks
        broadcasts: List[asyncio.Task] = []
        for api in ws_cfg.get("apis", []):
            if api.get("broadcast"):
                full = f"{prefix}{api['path']}"
                broadcasts.append(asyncio.create_task(self._broadcast_loop(full, api["broadcast"])))
        try:
            await asyncio.gather(server.wait_closed(), *broadcasts)
        finally:
            for b in broadcasts:
                b.cancel()

    async def _ws_client(self, websocket, path: str):
        api_cfg = self.ws_path_cfg.get(path)
        if not api_cfg:
            await websocket.close(code=4004, reason="Path not found")
            return
            
        # normalize deprecated alias for rules
        if "rules" not in api_cfg and "triggers" in api_cfg:
            if not self.actions.deprecation_logged:
                logger.warning("WS config key 'triggers' is deprecated; use 'rules' instead.")
                self.actions.deprecation_logged = True
            api_cfg = {**api_cfg, "rules": api_cfg.get("triggers")}
            
        api = WebSocketApiConfig(**api_cfg)
        cid = str(id(websocket))
        self.ws_clients.setdefault(path, set()).add(websocket)
        self.client_states[cid] = {"connect_time": time.time(), "path": path}
        
        try:
            async for raw in websocket:
                if self.actions.is_blocked(cid):
                    continue
                try:
                    msg = json.loads(raw)
                except Exception:
                    msg = {"raw": raw}
                ctx = {"message": msg, "client_state": self.client_states[cid]}
                initial = self.engine.render(api.response) if api.response else None
                resp, ok, meta = await self.triggers.process(api.rules, ctx, initial, websocket)
                if ok and resp is not None:
                    await websocket.send(json.dumps(resp))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.ws_clients.get(path, set()).discard(websocket)
            self.client_states.pop(cid, None)

    async def _broadcast_loop(self, path: str, cfg: Dict[str, Any]):
        interval = float(cfg.get("interval", 1.0))
        logger.info("WS broadcast %s every %ss", path, interval)
        while True:
            await asyncio.sleep(interval)
            clients = list(self.ws_clients.get(path, set()))
            if not clients: continue
            
            # allow rules on broadcast payloads as well
            base = self.engine.render(cfg.get("response", {}))
            rules = cfg.get("rules")
            if rules:
                # no inbound message; use minimal context
                ctx = {"message": {}, "client_state": {}}
                base, should_send, meta = await self.triggers.process(rules, ctx, base, websocket=None)
                if not should_send:
                    continue
            payload = base
            data = json.dumps(payload)
            results = await asyncio.gather(*(c.send(data) for c in clients), return_exceptions=True)
            for c, r in zip(clients, results):
                if isinstance(r, Exception):
                    self.ws_clients.get(path, set()).discard(c)

    # ----------------- GraphQL WS (graphql-transport-ws subset) -----------------
    async def _ws_graphql(self, websocket):
        """
        Minimal graphql-transport-ws:
        Client: {"type":"connection_init"} -> Server: {"type":"connection_ack"}
        Client: {"id":"1","type":"subscribe","payload":{"operationName":"SubName"}}
        Server: {"id":"1","type":"next","payload":{"data":<rendered>}} (repeats)
        Client: {"id":"1","type":"complete"} -> stop
        Also handle {"type":"ping"} -> {"type":"pong"}.
        """
        subs: Dict[str, asyncio.Task] = {}
        try:
            async for raw in websocket:
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                mtype = msg.get("type")
                if mtype == "connection_init":
                    await websocket.send(json.dumps({"type":"connection_ack"}))
                elif mtype == "ping":
                    await websocket.send(json.dumps({"type":"pong"}))
                elif mtype == "subscribe":
                    sid = msg.get("id") or str(uuid.uuid4())
                    op = ((msg.get("payload") or {}).get("operationName"))
                    entry = self.gql_subscriptions.get(op)
                    if not entry:
                        # Send a GraphQL-compliant error frame (simple)
                        err = {"id": sid, "type":"error", "payload":{"message": f"Unknown subscription '{op}'"}}
                        await websocket.send(json.dumps(err))
                        continue
                    interval = float(entry.get("interval", 1.0))
                    rules = entry.get("rules")
                    template = entry.get("response", {})
                    
                    async def loop():
                        while True:
                            with self.engine.use({"headers":{}, "query":{}, "path":{}, "method":"SUBSCRIBE", "body":{}}):
                                data = self.engine.render(template)
                                if rules:
                                    data, ok, meta = await self.triggers.process(rules, {}, data, websocket=None)
                                    if not ok:
                                        await asyncio.sleep(interval)
                                        continue
                            await websocket.send(json.dumps({"id": sid, "type":"next", "payload":{"data": data}}))
                            await asyncio.sleep(interval)
                            
                    task = asyncio.create_task(loop())
                    subs[sid] = task
                elif mtype == "complete":
                    sid = msg.get("id")
                    t = subs.pop(sid, None)
                    if t: t.cancel()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            for t in subs.values():
                t.cancel()

    # ----------------- UDP -----------------
    async def _udp_loop(self, api_cfg: Dict[str, Any], host: str, port: int):
        api = UdpApiConfig(**api_cfg)
        name = api.name or str(uuid.uuid4())
        interval = float(api.broadcast.interval)
        
        # Test-only UDP target override via environment
        import os
        override = os.getenv("APISIM_UDP_TARGET")
        if override:
            host, port = override.rsplit(":", 1)
            port = int(port)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info("UDP '%s' -> %s:%d every %.3fs", name, host, port, interval)
        while True:
            await asyncio.sleep(interval)
            payload = self.engine.render(api.broadcast.response)
            body = msgpack.packb(payload)
            header = struct.pack(">IIH", 0xDEADBEEF, int(time.time()), len(body))
            pkt = header + body
            try:
                sock.sendto(pkt, (host, port))
            except OSError as e:
                logger.warning("UDP send error: %s", e)

    # -------------- TLS helpers --------------
    def enable_tls(self, certfile: str, keyfile: str) -> None:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(certfile, keyfile)
        self.ssl_context = ctx

# ---------- helpers ----------
def resolve_http_port(cfg: Dict[str, Any]) -> int:
    rest = (cfg.get("rest") or {})
    gql = (cfg.get("graphql") or {})
    return int(rest.get("port") or gql.get("port") or 8000)