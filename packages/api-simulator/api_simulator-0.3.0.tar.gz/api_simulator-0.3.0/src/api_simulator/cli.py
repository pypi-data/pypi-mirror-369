from __future__ import annotations
import argparse
import json
import logging
import uvicorn
from typing import Any, Dict

from .app import APISimulator, resolve_http_port
from .schema import validate_config
from .templates import TemplateEngine


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_validate(args: argparse.Namespace) -> int:
    cfg = _load_json(args.config)
    try:
        validate_config(cfg)
    except Exception as e:
        print(f"❌ invalid config: {e}")
        return 2
    print("✅ config valid")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    cfg = _load_json(args.config)
    if args.validate:
        validate_config(cfg)

    engine = TemplateEngine(seed=args.seed)
    if args.templates:
        t = _load_json(args.templates)
        engine.load_macros((t or {}).get("functions", {}))

    sim = APISimulator(cfg, engine=engine)

    # WSS if TLS provided
    if args.certfile and args.keyfile:
        sim.enable_tls(args.certfile, args.keyfile)

    http_port = args.port or resolve_http_port(cfg)

    logging.basicConfig(
        level=getattr(logging, (args.log_level or "INFO").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    print(f"HTTP listening on {'https' if args.certfile else 'http'}://{args.host}:{http_port}")
    if cfg.get("websocket"):
        proto = "wss" if args.certfile else "ws"
        print(f"WebSocket on {proto}://{args.host}:{cfg['websocket']['port']}{cfg['websocket'].get('path','')}")
        gql = (cfg.get("graphql") or {})
        if gql.get("subscriptions"):
            ws_path = (gql.get("subscriptions_path")
                       or f"{cfg['websocket'].get('path','')}/graphql")
            print(f"GraphQL subscriptions at {proto}://{args.host}:{cfg['websocket']['port']}{ws_path}")

    uvicorn.run(
        sim.app,
        host=args.host,
        port=http_port,
        log_level=(args.log_level or "info").lower(),
        ssl_certfile=args.certfile,
        ssl_keyfile=args.keyfile,
    )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show running apisim servers and their ports"""
    import subprocess
    import re
    
    try:
        # Get all apisim processes
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        servers = []
        for line in result.stdout.split('\n'):
            if 'apisim run' in line and 'grep' not in line:
                # Extract PID
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    
                    # Try to extract config file
                    config_match = re.search(r'--config\s+(\S+)', line)
                    config = config_match.group(1) if config_match else "unknown"
                    
                    # Get listening ports for this PID
                    lsof_result = subprocess.run(
                        ["lsof", "-Pan", "-p", pid, "-i"], 
                        capture_output=True, 
                        text=True
                    )
                    
                    ports = []
                    for lsof_line in lsof_result.stdout.split('\n'):
                        if 'LISTEN' in lsof_line:
                            port_match = re.search(r':(\d+)', lsof_line)
                            if port_match:
                                ports.append(port_match.group(1))
                    
                    servers.append({
                        'pid': pid,
                        'config': config,
                        'ports': ports
                    })
        
        if not servers:
            print("No apisim servers running")
            return 0
            
        print("Running apisim servers:")
        print("-" * 60)
        for srv in servers:
            print(f"PID: {srv['pid']}")
            print(f"Config: {srv['config']}")
            if srv['ports']:
                print(f"Ports: {', '.join(srv['ports'])}")
                # Map common ports to protocols
                for port in srv['ports']:
                    if port == "3000" or port == "8000":
                        print(f"  - :{port} (REST/GraphQL)")
                    elif port == "9080":
                        print(f"  - :{port} (WebSocket)")
            print("-" * 60)
            
    except Exception as e:
        print(f"Error checking status: {e}")
        return 1
    
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    """Stop running apisim servers"""
    import subprocess
    import signal
    
    try:
        # Get all apisim processes
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        pids = []
        for line in result.stdout.split('\n'):
            if 'apisim run' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    pids.append(parts[1])
        
        if not pids:
            print("No apisim servers running")
            return 0
        
        if args.all:
            # Stop all servers
            for pid in pids:
                try:
                    subprocess.run(["kill", "-TERM", pid])
                    print(f"Stopped apisim server (PID: {pid})")
                except Exception as e:
                    print(f"Failed to stop PID {pid}: {e}")
        else:
            # Interactive selection if multiple servers
            if len(pids) == 1:
                pid = pids[0]
            else:
                print("Multiple apisim servers running:")
                for i, pid in enumerate(pids, 1):
                    print(f"  {i}. PID: {pid}")
                
                try:
                    choice = input("Which one to stop? (number or 'all'): ").strip()
                    if choice.lower() == 'all':
                        for pid in pids:
                            subprocess.run(["kill", "-TERM", pid])
                            print(f"Stopped apisim server (PID: {pid})")
                        return 0
                    else:
                        idx = int(choice) - 1
                        if 0 <= idx < len(pids):
                            pid = pids[idx]
                        else:
                            print("Invalid selection")
                            return 1
                except (ValueError, EOFError, KeyboardInterrupt):
                    print("\nCancelled")
                    return 1
            
            subprocess.run(["kill", "-TERM", pid])
            print(f"Stopped apisim server (PID: {pid})")
            
    except Exception as e:
        print(f"Error stopping servers: {e}")
        return 1
    
    return 0


def main() -> None:
    p = argparse.ArgumentParser(prog="apisim", description="Multi-protocol API simulator")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="Validate a config.json against the schema")
    pv.add_argument("--config", required=True)
    
    # Status command
    ps = sub.add_parser("status", help="Show running apisim servers")
    
    # Stop command
    pst = sub.add_parser("stop", help="Stop running apisim servers")
    pst.add_argument("--all", action="store_true", help="Stop all running servers")

    # OpenAPI exporter
    po = sub.add_parser("openapi", help="OpenAPI utilities")
    so = po.add_subparsers(dest="openapi_cmd", required=True)
    po1 = so.add_parser("export", help="Export OpenAPI JSON from config")
    po1.add_argument("--config", required=True)
    po1.add_argument("--out", default="openapi.json")
    po1.add_argument("--title", default="API Simulator")
    po1.add_argument("--version", default="0.3.0")
    po1.add_argument("--server-url", help="Base URL for 'servers[0].url' (e.g., http://localhost:3000)")
    po1.add_argument("--include-extensions", action="store_true", help="Include x-simulator metadata for WS/UDP")

    pr = sub.add_parser("run", help="Run the simulator")
    pr.add_argument("--config", required=True)
    pr.add_argument("--templates", help="Optional templates.json (macros)")
    pr.add_argument("--seed", type=int, default=None, help="Seed for deterministic randomness")
    pr.add_argument("--host", default="0.0.0.0")
    pr.add_argument("--port", type=int)
    pr.add_argument("--log-level", default="INFO")
    pr.add_argument("--validate", action="store_true", help="Validate before running")
    pr.add_argument("--certfile", help="Path to TLS cert for HTTPS/WSS")
    pr.add_argument("--keyfile", help="Path to TLS key for HTTPS/WSS")

    args = p.parse_args()

    if args.cmd == "validate":
        raise SystemExit(cmd_validate(args))
    elif args.cmd == "status":
        raise SystemExit(cmd_status(args))
    elif args.cmd == "stop":
        raise SystemExit(cmd_stop(args))
    elif args.cmd == "openapi" and args.openapi_cmd == "export":
        from .openapi import build_openapi
        cfg = _load_json(args.config)
        spec = build_openapi(cfg, title=args.title, version=args.version, server_url=args.server_url,
                             include_extensions=args.include_extensions)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)
        print(f"✅ OpenAPI written to {args.out}")
        raise SystemExit(0)
    elif args.cmd == "run":
        raise SystemExit(cmd_run(args))