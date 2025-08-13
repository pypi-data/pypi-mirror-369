# orchestration.py
"""
Top-level pattern/session tracing + pause-before-next + message injection.
Now with:
- Stable record IDs
- Server-Sent Events (SSE) push updates (no flicker)
- Preact-based keyed UI (via ui/monitor.html + ui/monitor.js)
- Light theme only

Behavior (pause-before-next):
- Click "Pause" -> the *next* top-level @pattern call blocks at entry.
- While blocked, you can Inject messages to any agent (always appended to end).
- Click "Resume" -> queued injections are drained into agent params, 'before' is snapshotted,
  pattern runs, 'after' is snapshotted, record marked done.

HTTP endpoints:
  GET  /              -> ui/monitor.html (bundled next to this file)
  GET  /static/*      -> files under ui/
  GET  /records       -> initial state {records, paused}
  GET  /events        -> SSE stream of events: record-start, record-finish, paused
  POST /pause         -> {}
  POST /resume        -> {}
  POST /inject        -> {"agent_id","text"} -> {}
"""

import inspect
import copy
import json
import threading
from collections import defaultdict
from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import mimetypes
import os
from typing import Optional
import queue
import time
from .messages import normalize_messages_for_display

# ---- session state ----
_current_session = ContextVar("current_session", default=None)


class Session:
    """Holds top-level pattern records, control plane, and an SSE broadcaster."""
    def __init__(self):
        # Each record: {
        #   id: int,
        #   pattern: str,
        #   status: "running"|"done",
        #   inputs: dict,
        #   agents: {param_name: {id, before, after|None}},
        #   result: any | None
        # }
        self.records = []
        self.depth = 0
        self._lock = threading.RLock()

        # Pause-before-next + inbox (agent_id -> [text, ...])
        self.pause_event = threading.Event()
        self.inbox = defaultdict(list)

        # SSE broadcaster: list of per-client queues
        self._clients = []
        self._next_id = 1

    # ---- SSE broadcaster helpers ----
    def _publish(self, event: dict):
        """Broadcast a dict event to all connected SSE clients."""
        with self._lock:
            clients = list(self._clients)
        for q in clients:
            try:
                q.put_nowait(event)
            except queue.Full:
                # drop if a client is too slow
                pass

    def add_client(self, maxsize: int = 100) -> queue.Queue:
        q = queue.Queue(maxsize=maxsize)
        with self._lock:
            self._clients.append(q)
        return q

    def remove_client(self, q: queue.Queue):
        with self._lock:
            if q in self._clients:
                self._clients.remove(q)

    # ---- recording ----
    def _next_rec_id(self) -> int:
        with self._lock:
            rid = self._next_id
            self._next_id += 1
            return rid

    def begin_record(self, rec: dict) -> int:
        """Append a running record and publish record-start."""
        if "id" not in rec or rec["id"] is None:
            rec["id"] = self._next_rec_id()
        with self._lock:
            self.records.append(rec)
            idx = len(self.records) - 1
        # Publish 'record-start' with light coercion (ensure JSON-compat)
        self._publish({"type": "record-start", "record": _coerce_record_jsonable(rec)})
        return idx

    def finish_record(self, idx: int, after_map: dict, result):
        """Fill 'after' and result, mark done, publish record-finish."""
        with self._lock:
            if 0 <= idx < len(self.records):
                rec = self.records[idx]
                for name, meta in rec.get("agents", {}).items():
                    meta["after"] = after_map.get(name)
                rec["result"] = result
                rec["status"] = "done"
                out = _coerce_record_jsonable(rec)
        # publish outside lock
        self._publish({"type": "record-finish", "record": out})

    def snapshot_records(self):
        # deep copy for safe serving
        with self._lock:
            return copy.deepcopy(self.records)

    # ---- control plane ----
    def request_pause(self):
        self.pause_event.set()
        self._publish({"type": "paused", "value": True})

    def clear_pause(self):
        self.pause_event.clear()
        self._publish({"type": "paused", "value": False})

    def is_paused(self) -> bool:
        return self.pause_event.is_set()

    def inject(self, agent_id: str, text: str):
        # Always append to end (no position support by design)
        if not text:
            return
        with self._lock:
            self.inbox[agent_id or "unnamed"].append(text)
        # optional: could publish an 'injected' event with counts

    def drain_into(self, agent) -> int:
        """Append queued injections (if any) to the end of agent.messages. Returns count drained."""
        aid = getattr(agent, "id", None) or "unnamed"
        with self._lock:
            pending = self.inbox.get(aid, [])
            self.inbox[aid] = []
        drained = 0
        for text in pending:
            if hasattr(agent, "add_user_message"):
                agent.add_user_message(text, position="end")  # force append
            else:
                agent.messages.append({"role": "user", "content": text})
            drained += 1
        return drained

    def wait_gate(self, agents: dict):
        """Pause-before-next gate. Blocks while paused, then drains injections BEFORE 'before' snapshot."""
        while self.is_paused():
            time.sleep(0.05)
        for ag in agents.values():
            self.drain_into(ag)

    def __str__(self):
        lines = []
        for rec in self.records:
            lines.append(f"------------- {rec['pattern']} ({rec.get('status','?')}) -------------")
            for param_name, meta in rec["agents"].items():
                agent_id = meta.get("id") or "unnamed"
                lines.append(f"{param_name}: {agent_id}")
            lines.append("")  # blank line between blocks
        named_ids = {
            meta["id"]
            for rec in self.records
            for meta in rec["agents"].values()
            if meta.get("id")
        }
        lines.append("------------- statistics -------------")
        lines.append(f"number of named agents: {len(named_ids)}")
        lines.append(f"number of patterns executed: {len(self.records)}")
        return "\n".join(lines)


@contextmanager
def session():
    """with session() as s: ...  s.records has snapshots for top-level patterns only."""
    s = Session()
    token = _current_session.set(s)
    try:
        yield s
    finally:
        _current_session.reset(token)


# ---- helpers ----
def _is_agent(x):
    # Minimal duck-typing: anything with a 'messages' attribute counts as an agent.
    return hasattr(x, "messages")


def _coerce_jsonable(x):
    try:
        json.dumps(x)
        return x
    except TypeError:
        return repr(x)


def _coerce_record_jsonable(rec: dict) -> dict:
    """Deep-ish coercion to keep SSE payloads JSON serializable."""
    out = copy.deepcopy(rec)
    if "inputs" in out:
        out["inputs"] = {
            k: (v if isinstance(v, (str, int, float, bool, list, dict, type(None))) else repr(v))
            for k, v in out["inputs"].items()
        }
    if "result" in out:
        out["result"] = _coerce_jsonable(out["result"])
    return out


def pattern(func):
    """Decorator: tracks pattern execution in session context if available, otherwise runs normally."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        s: Session = _current_session.get()
        
        # If no session context, just run the function normally
        if s is None:
            return func(*args, **kwargs)
        
        # Session context exists - do tracking
        is_top_level = (s.depth == 0)
        s.depth += 1
        rec_idx = None
        try:
            if not is_top_level:
                return func(*args, **kwargs)

            # Bind args to names so we can split agent vs non-agent params.
            bound = inspect.signature(func).bind_partial(*args, **kwargs)
            bound.apply_defaults()
            agents = {k: v for k, v in bound.arguments.items() if _is_agent(v)}
            inputs = {k: v for k, v in bound.arguments.items() if k not in agents}

            # Pause gate then drain queued injections
            s.wait_gate(agents)

            # Snapshot before (normalized for display)
            snap_before = {name: normalize_messages_for_display(ag.messages) for name, ag in agents.items()}

            # Publish a "running" record immediately (and store it)
            running_rec = {
                "id": None,  # assigned in begin_record
                "pattern": func.__name__,
                "status": "running",
                "inputs": inputs,
                "agents": {
                    name: {
                        "id": (getattr(ag, "id", None) or None),
                        "before": snap_before[name],
                        "after": None,
                    } for name, ag in agents.items()
                },
                "result": None,
            }
            rec_idx = s.begin_record(running_rec)

            # Execute pattern
            result = func(*args, **kwargs)

            # Snapshot after and finish the record (normalized for display)
            snap_after = {name: normalize_messages_for_display(ag.messages) for name, ag in agents.items()}
            s.finish_record(rec_idx, snap_after, result)

            return result
        finally:
            s.depth -= 1
    return wrapper


# ---- HTTP server (serves packaged UI + SSE) ----

def serve_session(s: Session, host: str = "127.0.0.1", port: int = 8765):
    """
    Start a tiny HTTP server to display current session records and accept controls.
    Serves a bundled light-theme UI from ./ui/ next to this file.
    Returns (server, thread).
    """
    session_ref = s  # capture in closure

    PKG_DIR = os.path.dirname(__file__)
    STATIC_DIR = os.path.join(PKG_DIR, "ui")
    UI_FILE = os.path.join(STATIC_DIR, "monitor.html")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # silence access logs
            return

        def _send_bytes(self, status: int, ctype: str, data: bytes):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, obj):
            body = json.dumps(obj).encode("utf-8")
            self._send_bytes(200, "application/json; charset=utf-8", body)

        def do_GET(self):
            # UI index
            if self.path in ("/", "/index.html"):
                if os.path.exists(UI_FILE):
                    with open(UI_FILE, "rb") as f:
                        self._send_bytes(200, "text/html; charset=utf-8", f.read())
                else:
                    self._send_bytes(
                        200,
                        "text/html; charset=utf-8",
                        b"<!doctype html><body style='background:#f8fafc;color:#111;font-family:sans-serif;margin:20px'><h1>Top-level Pattern Calls</h1><p>Missing ui/monitor.html</p></body>",
                    )
                return

            # Static assets
            if self.path.startswith("/static/"):
                rel = self.path[len("/static/"):]
                safe_rel = os.path.normpath(rel).replace("\\", "/")
                if safe_rel.startswith(".."):
                    self.send_response(403); self.end_headers(); return
                fp = os.path.join(STATIC_DIR, safe_rel)
                if os.path.isfile(fp):
                    ctype, _ = mimetypes.guess_type(fp)
                    ctype = ctype or "application/octet-stream"
                    with open(fp, "rb") as f:
                        self._send_bytes(200, ctype, f.read())
                else:
                    self.send_response(404); self.end_headers()
                return

            # Initial data
            if self.path == "/records":
                data = session_ref.snapshot_records()
                # Coerce JSONability
                data = [_coerce_record_jsonable(r) for r in data]
                self._send_json({"records": data, "paused": session_ref.is_paused()})
                return

            # SSE stream
            if self.path == "/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()

                q = session_ref.add_client()
                # send initial paused state event
                try:
                    init_evt = {"type": "paused", "value": session_ref.is_paused()}
                    self.wfile.write(b"data: " + json.dumps(init_evt).encode("utf-8") + b"\n\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError) as e:
                    # Client disconnected during initial setup
                    session_ref.remove_client(q)
                    return
                except Exception as e:
                    print(f"SSE: Error sending initial event: {e}")
                    session_ref.remove_client(q)
                    return

                try:
                    while True:
                        try:
                            evt = q.get(timeout=15.0)
                            payload = json.dumps(evt).encode("utf-8")
                            self.wfile.write(b"data: " + payload + b"\n\n")
                            self.wfile.flush()
                        except queue.Empty:
                            # keep-alive comment
                            try:
                                self.wfile.write(b": keep-alive\n\n")
                                self.wfile.flush()
                            except (BrokenPipeError, ConnectionResetError):
                                # Client disconnected
                                break
                            except Exception as e:
                                print(f"SSE: Error sending keep-alive: {e}")
                                break
                except (BrokenPipeError, ConnectionResetError):
                    # Normal client disconnection
                    pass
                except Exception as e:
                    print(f"SSE: Unexpected error in event loop: {e}")
                finally:
                    session_ref.remove_client(q)
                return

            self.send_response(404); self.end_headers()

        def do_POST(self):
            def read_json():
                n = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(n) if n else b""
                try:
                    return json.loads(raw.decode("utf-8")) if raw else {}
                except Exception:
                    return {}

            if self.path == "/pause":
                session_ref.request_pause()
                self._send_json({})
                return

            if self.path == "/resume":
                session_ref.clear_pause()
                self._send_json({})
                return

            if self.path == "/inject":
                payload = read_json()
                agent_id = payload.get("agent_id") or "unnamed"
                text = payload.get("text") or ""
                session_ref.inject(agent_id, text)
                self._send_json({})
                return

            self.send_response(404); self.end_headers()

    server = ThreadingHTTPServer((host, port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t

