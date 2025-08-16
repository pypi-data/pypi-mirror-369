from __future__ import annotations
import ast
import random
import time
import uuid as _uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
import re
from contextlib import contextmanager

Token = Tuple[int, int, str]

FUNC_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*(\((.*)\))?$")
VAR_RE = re.compile(r"\{\{\s*(.*?)\s*\}\}")


def _literal_eval_list(args_src: str) -> Tuple[List[Any], Dict[str, Any]]:
    """Parse args_src into (args, kwargs) using literal_eval safely."""
    if not args_src or args_src.strip() == "":
        return [], {}
    expr = ast.parse(f"f({args_src})", mode="eval")
    call = expr.body  # type: ignore[attr-defined]
    if not isinstance(call, ast.Call):
        raise ValueError("Invalid arguments")
    def lit(node: ast.AST) -> Any:
        return ast.literal_eval(node)
    args = [lit(a) for a in call.args]
    kwargs = {kw.arg: lit(kw.value) for kw in call.keywords if kw.arg is not None}
    return args, kwargs


@dataclass
class TemplateEngine:
    seed: Optional[int] = None
    macros: Dict[str, str] = field(default_factory=dict)  # name -> expression string (e.g., "counter('id')")

    def __post_init__(self) -> None:
        self.random = random.Random(self.seed)
        self.counters: Dict[str, int] = {}
        self.ctx: Dict[str, Any] = {}
        # built-in function registry
        self.funcs: Dict[str, Callable[..., Any]] = {
            # data/time/randomness
            "timestamp": self.timestamp,
            "unix_timestamp": self.unix_timestamp,
            "uuid4": self.uuid4,
            "random_int": self.random_int,
            "random_float": self.random_float,
            "uniform": self.uniform,
            "choice": self.choice,
            "counter": self.counter,
            "random_price": self.random_price,
            # request-context helpers
            "header": self.header,
            "query": self.query,
            "path": self.pathvar,
            "body": self.body,
            "method": self.method,
        }

    # ---------- built-ins ----------
    def timestamp(self) -> str:
        return datetime.now().isoformat()

    def unix_timestamp(self) -> int:
        return int(time.time())

    def uuid4(self) -> str:
        return str(_uuid.uuid4())

    def random_int(self, a: int = 1, b: int = 1000) -> int:
        return self.random.randint(int(a), int(b))

    def random_float(self, a: float = 0.0, b: float = 100.0, ndigits: int = 2) -> float:
        return round(self.random.uniform(float(a), float(b)), int(ndigits))

    def uniform(self, a: float, b: float) -> float:
        return self.random.uniform(a, b)

    def choice(self, seq: List[Any]) -> Any:
        if not isinstance(seq, list) or len(seq) == 0:
            return None
        return self.random.choice(seq)

    def counter(self, name: str = "default", start: int = 0, step: int = 1) -> int:
        v = self.counters.get(name, start)
        self.counters[name] = v + step
        return v

    def random_price(self, min_price: float = 30000.0, max_price: float = 70000.0, ndigits: int = 2) -> float:
        return round(self.random.uniform(min_price, max_price), ndigits)

    # ---------- request-context helpers ----------
    @contextmanager
    def use(self, ctx: Dict[str, Any]):
        prev = self.ctx
        self.ctx = ctx or {}
        try:
            yield
        finally:
            self.ctx = prev

    def header(self, name: str, default: Any = None) -> Any:
        return (self.ctx.get("headers") or {}).get(name, default)

    def query(self, name: str, default: Any = None) -> Any:
        return (self.ctx.get("query") or {}).get(name, default)

    def pathvar(self, name: str, default: Any = None) -> Any:
        return (self.ctx.get("path") or {}).get(name, default)

    def body(self, name: Optional[str] = None, default: Any = None) -> Any:
        b = self.ctx.get("body")
        if name is None:
            return b
        if isinstance(b, dict):
            return b.get(name, default)
        return default

    def method(self) -> str:
        return (self.ctx.get("method") or "").upper()

    # ---------- engine ----------
    def register(self, name: str, func: Callable[..., Any]) -> None:
        self.funcs[name] = func

    def load_macros(self, macros: Dict[str, str]) -> None:
        self.macros.update(macros or {})

    def _eval_token(self, token: str) -> Any:
        m = FUNC_RE.match(token)
        if not m:
            if token in self.macros:
                return self._eval_call(self.macros[token])
            return f"{{{{{token}}}}}"
        name, _, args_src = m.group(1), m.group(2), m.group(3)
        if args_src is None and token in self.macros:
            return self._eval_call(self.macros[token])
        if name not in self.funcs:
            if name in self.macros:
                return self._eval_call(self.macros[name])
            return f"{{{{{token}}}}}"
        args, kwargs = _literal_eval_list(args_src or "")
        return self.funcs[name](*args, **kwargs)

    def _eval_call(self, expr: str) -> Any:
        mm = FUNC_RE.match(expr.strip())
        if not mm:
            return expr
        fname, _, args_src = mm.group(1), mm.group(2), mm.group(3)
        if fname not in self.funcs:
            return expr
        args, kwargs = _literal_eval_list(args_src or "")
        return self.funcs[fname](*args, **kwargs)

    def _replace_once(self, s: Any) -> Any:
        if isinstance(s, dict):
            return {k: self._replace_once(v) for k, v in s.items()}
        if isinstance(s, list):
            return [self._replace_once(v) for v in s]
        if not isinstance(s, str):
            return s
        def repl(m: re.Match[str]) -> str:
            token = m.group(1)
            val = self._eval_token(token)
            return str(val)
        return VAR_RE.sub(repl, s)

    def render(self, obj: Any, max_passes: int = 2) -> Any:
        out = obj
        for _ in range(max_passes):
            out_next = self._replace_once(out)
            if out_next == out:
                break
            out = out_next
        return out