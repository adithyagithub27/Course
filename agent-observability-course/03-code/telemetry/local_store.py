"""SQLite span store + JSONL import/export for offline mode and the Ops Console.

Both the OpenTelemetry exporter (live traffic) and the replay simulator write
:class:`SpanRecord` rows here, so every analysis (cost, latency, quality,
budgets) reads one schema whether the data came from real spans or a replay.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from northwind.cost import CostRecord
from northwind.latency import LatencySample

#: Observation kinds stored in ``kind`` (mirrors Langfuse observation types).
KINDS: tuple[str, ...] = ("agent", "generation", "tool", "retriever", "guardrail", "span")

# Attribute keys we index as columns for fast grouping.
ATTR_TENANT = "atlas.tenant"
ATTR_FEATURE = "atlas.feature"
ATTR_INTENT = "atlas.intent"
ATTR_COST = "atlas.cost_usd"
ATTR_SCENARIO = "atlas.scenario"
ATTR_OUTCOME = "atlas.outcome"
ATTR_STEPS = "atlas.steps"
ATTR_TTFT_MS = "atlas.ttft_ms"
ATTR_PROMPT_VERSION = "atlas.prompt_version"
ATTR_SESSION = "session.id"
ATTR_USER = "user.id"
ATTR_MODEL = "gen_ai.request.model"
ATTR_TOOL = "gen_ai.tool.name"
ATTR_IN = "gen_ai.usage.input_tokens"
ATTR_OUT = "gen_ai.usage.output_tokens"
ATTR_CACHED = "gen_ai.usage.cache_read.input_tokens"
ATTR_LF_TYPE = "langfuse.observation.type"


@dataclass
class SpanRecord:
    """A flattened span. Times are epoch seconds (float)."""

    trace_id: str
    span_id: str
    name: str
    kind: str
    start_time: float
    end_time: float
    parent_span_id: str | None = None
    status: str = "OK"
    attributes: dict[str, Any] = field(default_factory=dict)
    resource: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        return max(0.0, (self.end_time - self.start_time) * 1000.0)

    def attr(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> SpanRecord:
        d = json.loads(line)
        return cls(**d)


@dataclass(frozen=True)
class ScoreRecord:
    trace_id: str
    name: str
    value: float
    source: str = "judge"  # judge | user | heuristic
    comment: str = ""
    timestamp: float = 0.0
    tenant: str = ""
    session_id: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS spans (
  trace_id TEXT NOT NULL,
  span_id TEXT NOT NULL PRIMARY KEY,
  parent_span_id TEXT,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL NOT NULL,
  duration_ms REAL NOT NULL,
  status TEXT NOT NULL,
  tenant TEXT, session_id TEXT, user_id TEXT, model TEXT, tool TEXT,
  feature TEXT, intent TEXT, scenario TEXT, outcome TEXT,
  input_tokens INTEGER, output_tokens INTEGER, cached_tokens INTEGER,
  cost_usd REAL,
  attributes TEXT NOT NULL, resource TEXT NOT NULL, events TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_spans_trace ON spans(trace_id);
CREATE INDEX IF NOT EXISTS idx_spans_kind_time ON spans(kind, start_time);
CREATE INDEX IF NOT EXISTS idx_spans_tenant ON spans(tenant);
CREATE TABLE IF NOT EXISTS scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trace_id TEXT NOT NULL, name TEXT NOT NULL, value REAL NOT NULL,
  source TEXT NOT NULL, comment TEXT, timestamp REAL NOT NULL,
  tenant TEXT, session_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_scores_trace ON scores(trace_id);
"""


class LocalSpanStore:
    """Thread-safe SQLite store. Use ``":memory:"`` for tests."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=MEMORY")
        self._conn.execute("PRAGMA synchronous=OFF")
        self._conn.executescript(_SCHEMA)

    # ---- writes -----------------------------------------------------------------
    @staticmethod
    def _row(r: SpanRecord) -> tuple[Any, ...]:
        a = r.attributes
        return (
            r.trace_id,
            r.span_id,
            r.parent_span_id,
            r.name,
            r.kind,
            r.start_time,
            r.end_time,
            r.duration_ms,
            r.status,
            a.get(ATTR_TENANT),
            a.get(ATTR_SESSION),
            a.get(ATTR_USER),
            a.get(ATTR_MODEL),
            a.get(ATTR_TOOL),
            a.get(ATTR_FEATURE),
            a.get(ATTR_INTENT),
            a.get(ATTR_SCENARIO),
            a.get(ATTR_OUTCOME),
            a.get(ATTR_IN),
            a.get(ATTR_OUT),
            a.get(ATTR_CACHED),
            a.get(ATTR_COST),
            json.dumps(a, sort_keys=True, default=str),
            json.dumps(r.resource, sort_keys=True, default=str),
            json.dumps(r.events, sort_keys=True, default=str),
        )

    def insert(self, records: Iterable[SpanRecord]) -> int:
        rows = [self._row(r) for r in records]
        if not rows:
            return 0
        with self._lock:
            self._conn.executemany(
                "INSERT OR REPLACE INTO spans VALUES (" + ",".join("?" * 25) + ")", rows
            )
            self._conn.commit()
        return len(rows)

    def add_score(self, score: ScoreRecord) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO scores(trace_id,name,value,source,comment,timestamp,tenant,session_id) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (
                    score.trace_id,
                    score.name,
                    score.value,
                    score.source,
                    score.comment,
                    score.timestamp,
                    score.tenant,
                    score.session_id,
                ),
            )
            self._conn.commit()

    def clear(self) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM spans")
            self._conn.execute("DELETE FROM scores")
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # ---- reads ------------------------------------------------------------------
    def count(self, kind: str | None = None) -> int:
        with self._lock:
            if kind:
                cur = self._conn.execute("SELECT COUNT(*) FROM spans WHERE kind=?", (kind,))
            else:
                cur = self._conn.execute("SELECT COUNT(*) FROM spans")
            return int(cur.fetchone()[0])

    def _rows_to_records(self, cur: sqlite3.Cursor) -> Iterator[SpanRecord]:
        for row in cur:
            yield SpanRecord(
                trace_id=row[0],
                span_id=row[1],
                parent_span_id=row[2],
                name=row[3],
                kind=row[4],
                start_time=row[5],
                end_time=row[6],
                status=row[8],
                attributes=json.loads(row[22]),
                resource=json.loads(row[23]),
                events=json.loads(row[24]),
            )

    def spans(
        self,
        *,
        kind: str | None = None,
        since: float | None = None,
        until: float | None = None,
        tenant: str | None = None,
        trace_id: str | None = None,
        limit: int | None = None,
    ) -> list[SpanRecord]:
        clauses, params = [], []
        if kind:
            clauses.append("kind=?")
            params.append(kind)
        if since is not None:
            clauses.append("start_time>=?")
            params.append(since)
        if until is not None:
            clauses.append("start_time<?")
            params.append(until)
        if tenant:
            clauses.append("tenant=?")
            params.append(tenant)
        if trace_id:
            clauses.append("trace_id=?")
            params.append(trace_id)
        sql = "SELECT * FROM spans"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY start_time, span_id"
        if limit:
            sql += f" LIMIT {int(limit)}"
        with self._lock:
            return list(self._rows_to_records(self._conn.execute(sql, params)))

    def trace(self, trace_id: str) -> list[SpanRecord]:
        return self.spans(trace_id=trace_id)

    def time_range(self) -> tuple[float, float]:
        with self._lock:
            row = self._conn.execute("SELECT MIN(start_time), MAX(end_time) FROM spans").fetchone()
        return (row[0] or 0.0, row[1] or 0.0)

    def cost_records(self, level: str = "generation", **filters: Any) -> list[CostRecord]:
        """Turn generation (per LLM call) or agent (per request) spans into CostRecords."""
        kind = "generation" if level == "generation" else "agent"
        out = []
        for s in self.spans(kind=kind, **filters):
            a = s.attributes
            out.append(
                CostRecord(
                    trace_id=s.trace_id,
                    tenant=str(a.get(ATTR_TENANT, "")),
                    model=str(a.get(ATTR_MODEL, "")),
                    input_tokens=int(a.get(ATTR_IN, 0) or 0),
                    output_tokens=int(a.get(ATTR_OUT, 0) or 0),
                    cached_tokens=int(a.get(ATTR_CACHED, 0) or 0),
                    reasoning_tokens=int(a.get("gen_ai.usage.reasoning.output_tokens", 0) or 0),
                    cost_usd=float(a.get(ATTR_COST, 0.0) or 0.0),
                    timestamp=s.start_time,
                    session_id=str(a.get(ATTR_SESSION, "")),
                    user_id=str(a.get(ATTR_USER, "")),
                    feature=str(a.get(ATTR_FEATURE, "chat")),
                    intent=str(a.get(ATTR_INTENT, "unknown")),
                    latency_ms=s.duration_ms,
                    outcome=str(a.get(ATTR_OUTCOME, "resolved" if s.status == "OK" else "error")),
                    steps=int(a.get(ATTR_STEPS, 1) or 1),
                    scenario=a.get(ATTR_SCENARIO),
                )
            )
        return out

    def latency_samples(self, **filters: Any) -> list[LatencySample]:
        out = []
        for s in self.spans(kind="agent", **filters):
            a = s.attributes
            out.append(
                LatencySample(
                    total_ms=s.duration_ms,
                    ttft_ms=a.get(ATTR_TTFT_MS),
                    output_tokens=int(a.get(ATTR_OUT, 0) or 0),
                    steps=int(a.get(ATTR_STEPS, 1) or 1),
                    trace_id=s.trace_id,
                    tenant=str(a.get(ATTR_TENANT, "")),
                    model=str(a.get(ATTR_MODEL, "")),
                )
            )
        return out

    def tool_stats(self) -> dict[str, dict[str, int]]:
        """Calls and errors per tool name."""
        stats: dict[str, dict[str, int]] = {}
        with self._lock:
            cur = self._conn.execute(
                "SELECT tool, status, COUNT(*) FROM spans WHERE kind='tool' GROUP BY tool, status"
            )
            for tool, status, n in cur:
                d = stats.setdefault(tool or "(unknown)", {"calls": 0, "errors": 0})
                d["calls"] += n
                if status == "ERROR":
                    d["errors"] += n
        return stats

    def scores(
        self, name: str | None = None, source: str | None = None, **filters: Any
    ) -> list[ScoreRecord]:
        clauses, params = [], []
        if name:
            clauses.append("name=?")
            params.append(name)
        if source:
            clauses.append("source=?")
            params.append(source)
        if filters.get("since") is not None:
            clauses.append("timestamp>=?")
            params.append(filters["since"])
        if filters.get("until") is not None:
            clauses.append("timestamp<?")
            params.append(filters["until"])
        sql = "SELECT trace_id,name,value,source,comment,timestamp,tenant,session_id FROM scores"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY timestamp, id"
        with self._lock:
            return [ScoreRecord(*row) for row in self._conn.execute(sql, params)]

    def score_values(self, name: str, **filters: Any) -> list[float]:
        return [s.value for s in self.scores(name=name, **filters)]

    # ---- JSONL ------------------------------------------------------------------
    def export_jsonl(self, path: str | Path, *, scores_path: str | Path | None = None) -> int:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        with p.open("w", encoding="utf-8") as fh:
            for s in self.spans():
                fh.write(s.to_json() + "\n")
                n += 1
        if scores_path is not None:
            with Path(scores_path).open("w", encoding="utf-8") as fh:
                for sc in self.scores():
                    fh.write(sc.to_json() + "\n")
        return n

    def import_jsonl(self, path: str | Path, *, scores_path: str | Path | None = None) -> int:
        recs = []
        with Path(path).open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    recs.append(SpanRecord.from_json(line))
        n = self.insert(recs)
        if scores_path is not None and Path(scores_path).exists():
            with Path(scores_path).open(encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        self.add_score(ScoreRecord(**json.loads(line)))
        return n

    @classmethod
    def from_jsonl(cls, path: str | Path, scores_path: str | Path | None = None) -> LocalSpanStore:
        store = cls(":memory:")
        store.import_jsonl(path, scores_path=scores_path)
        return store


def records_from_otel(spans: Sequence[Any]) -> list[SpanRecord]:
    """Convert OpenTelemetry ``ReadableSpan`` objects to :class:`SpanRecord`."""
    out = []
    for sp in spans:
        ctx = sp.get_span_context()
        attrs = dict(sp.attributes or {})
        kind = str(attrs.get(ATTR_LF_TYPE) or _infer_kind(sp.name, attrs))
        status_code = getattr(getattr(sp, "status", None), "status_code", None)
        status = getattr(status_code, "name", "UNSET") or "UNSET"
        if status == "UNSET":
            status = "OK"
        out.append(
            SpanRecord(
                trace_id=f"{ctx.trace_id:032x}",
                span_id=f"{ctx.span_id:016x}",
                parent_span_id=f"{sp.parent.span_id:016x}" if sp.parent else None,
                name=sp.name,
                kind=kind,
                start_time=(sp.start_time or 0) / 1e9,
                end_time=(sp.end_time or sp.start_time or 0) / 1e9,
                status=status,
                attributes={k: _jsonable(v) for k, v in attrs.items()},
                resource={k: _jsonable(v) for k, v in dict(sp.resource.attributes).items()},
                events=[
                    {
                        "name": e.name,
                        "time": e.timestamp / 1e9,
                        "attributes": dict(e.attributes or {}),
                    }
                    for e in (sp.events or [])
                ],
            )
        )
    return out


def _infer_kind(name: str, attrs: dict[str, Any]) -> str:
    op = str(attrs.get("gen_ai.operation.name", ""))
    if op in {"chat", "text_completion", "generate_content"}:
        return "generation"
    if op == "execute_tool":
        return "tool"
    if op == "invoke_agent":
        return "agent"
    if op == "retrieval":
        return "retriever"
    if name.startswith("guardrail"):
        return "guardrail"
    return "span"


def _jsonable(v: Any) -> Any:
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    return str(v)


class LocalStoreSpanExporter:
    """OpenTelemetry ``SpanExporter`` that writes into a :class:`LocalSpanStore`."""

    def __init__(self, store: LocalSpanStore) -> None:
        self.store = store

    def export(self, spans: Sequence[Any]) -> Any:
        from opentelemetry.sdk.trace.export import SpanExportResult

        try:
            self.store.insert(records_from_otel(spans))
            return SpanExportResult.SUCCESS
        except Exception:  # noqa: BLE001 - telemetry must never raise into the app
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True


class JsonlSpanExporter:
    """OpenTelemetry ``SpanExporter`` appending one JSON line per span."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def export(self, spans: Sequence[Any]) -> Any:
        from opentelemetry.sdk.trace.export import SpanExportResult

        try:
            with self._lock, self.path.open("a", encoding="utf-8") as fh:
                for r in records_from_otel(spans):
                    fh.write(r.to_json() + "\n")
            return SpanExportResult.SUCCESS
        except Exception:  # noqa: BLE001
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True
