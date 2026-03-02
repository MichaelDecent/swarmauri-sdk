from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from ..mapping import engine_resolver as _resolver

try:  # pragma: no cover
    from sqlalchemy import event, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.schema import CreateSchema  # type: ignore
except Exception:  # pragma: no cover
    event = text = CreateSchema = None  # type: ignore
    Engine = object  # type: ignore

from ..config.constants import __SAFE_IDENT__

__all__ = [
    "register_sqlite_attach",
    "ensure_schemas",
    "bootstrap_dbschema",
    "sqlite_default_attach_map",
    "initialize",
]


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------


def _quote_ident_sqlite(name: str) -> str:
    if __SAFE_IDENT__.match(name or ""):
        return name
    return '"' + (name or "").replace('"', '""') + '"'


def _attached_names_sqlite(dbapi_conn: Any) -> set[str]:
    names: set[str] = set()
    cur = None
    try:
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA database_list")
        for row in cur.fetchall():
            names.add(str(row[1]))
    finally:
        try:
            cur and cur.close()
        except Exception:
            pass
    return names


def _attach_sqlite_dbapi(dbapi_conn: Any, attachments: Mapping[str, str]) -> None:
    cur = None
    try:
        existing = _attached_names_sqlite(dbapi_conn)
        cur = dbapi_conn.cursor()
        try:
            cur.execute("PRAGMA foreign_keys=ON")
        except Exception:
            pass
        for schema, path in (attachments or {}).items():
            if not path or schema in existing:
                continue
            ident = _quote_ident_sqlite(schema)
            try:
                cur.execute(f"ATTACH DATABASE ? AS {ident}", (path,))
            except Exception:
                cur.execute(f"ATTACH DATABASE '{path}' AS {ident}")  # nosec: application-provided paths
    finally:
        try:
            cur and cur.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def sqlite_default_attach_map(engine: Engine, schemas: Iterable[str]) -> Dict[str, str]:
    """Return a deterministic SQLite ATTACH map for ``schemas``."""
    sync_engine = getattr(engine, "sync_engine", engine)
    db = getattr(getattr(sync_engine, "url", None), "database", None) or ":memory:"
    if db == ":memory:" or str(db).startswith("file::memory:"):
        return {s: ":memory:" for s in schemas}
    p = Path(db)
    suffix = p.suffix if p.suffix else ".db"
    return {s: str(p.with_name(f"{p.stem}__{s}{suffix}")) for s in schemas}


def register_sqlite_attach(engine: Engine, attachments: Mapping[str, str]) -> Any:
    sync_engine = getattr(engine, "sync_engine", engine)
    if (
        not hasattr(sync_engine, "dialect")
        or getattr(sync_engine.dialect, "name", "") != "sqlite"
    ):
        return None

    def _connect_listener(dbapi_conn, _):  # type: ignore[override]
        try:
            _attach_sqlite_dbapi(dbapi_conn, attachments)
        except Exception:
            pass

    event.listen(sync_engine, "connect", _connect_listener)
    return _connect_listener


def ensure_schemas(engine: Engine, schemas: Iterable[str]) -> Sequence[str]:
    if not schemas:
        return tuple()
    if not hasattr(engine, "dialect"):
        return tuple(schemas)

    dialect = getattr(engine.dialect, "name", "")
    attempted: list[str] = []

    if dialect == "sqlite":
        return tuple()

    if text is None:  # pragma: no cover
        raise RuntimeError("SQLAlchemy is required for ensure_schemas")

    try:
        with engine.begin() as conn:
            for name in dict.fromkeys(schemas).keys():
                if not name:
                    continue
                attempted.append(name)
                try:
                    conn.execute(CreateSchema(name))  # type: ignore[arg-type]
                except Exception:
                    try:
                        if dialect in ("postgresql", "redshift"):
                            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{name}"'))
                        elif dialect in ("mysql", "mariadb"):
                            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS `{name}`"))
                        elif dialect in ("mssql", "sqlserver"):
                            conn.execute(
                                text(
                                    "IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = :n) "
                                    "EXEC('CREATE SCHEMA ' + QUOTENAME(:n))"
                                ),
                                {"n": name},
                            )
                        else:
                            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {name}"))
                    except Exception:
                        pass
    except Exception:
        pass

    return tuple(attempted)


def bootstrap_dbschema(
    engine: Engine,
    *,
    schemas: Optional[Iterable[str]] = None,
    sqlite_attachments: Optional[Mapping[str, str]] = None,
    immediate: bool = True,
) -> Dict[str, Any]:
    attempted = tuple()
    if schemas:
        attempted = ensure_schemas(engine, schemas)

    listener = None
    if sqlite_attachments:
        listener = register_sqlite_attach(engine, sqlite_attachments)
        sync_engine = getattr(engine, "sync_engine", engine)
        if immediate and getattr(sync_engine.dialect, "name", "") == "sqlite":
            try:
                with sync_engine.connect() as conn:
                    dbapi = getattr(conn, "connection", None)
                    if dbapi is not None:
                        _attach_sqlite_dbapi(dbapi, sqlite_attachments)
            except Exception:
                pass

    return {
        "attempted_schemas": attempted,
        "sqlite_attachments": dict(sqlite_attachments or {}),
        "listener": listener,
    }


# ---------------------------------------------------------------------------
# Internal creation helper
# ---------------------------------------------------------------------------


def _create_all_on_bind(
    bind,
    *,
    schemas: Iterable[str] | None = None,
    sqlite_attachments: Mapping[str, str] | None = None,
    tables: Iterable[Any] | None = None,
) -> None:
    engine = getattr(bind, "engine", bind)
    tables = list(tables or [])

    if not hasattr(engine, "dialect"):
        return

    schema_names = set(schemas or [])
    for t in tables:
        if getattr(t, "schema", None):
            schema_names.add(t.schema)

    attachments = sqlite_attachments
    if attachments is None and getattr(engine.dialect, "name", "") == "sqlite":
        if schema_names:
            attachments = sqlite_default_attach_map(engine, schema_names)

    if attachments:
        bootstrap_dbschema(
            engine,
            schemas=schema_names,
            sqlite_attachments=attachments,
            immediate=True,
        )
    else:
        ensure_schemas(engine, schema_names)

    by_meta: dict[Any, list[Any]] = {}
    for t in tables:
        by_meta.setdefault(t.metadata, []).append(t)
    for md, group in by_meta.items():
        md.create_all(bind=bind, checkfirst=True, tables=group)


# ---------------------------------------------------------------------------
# Public initialize
# ---------------------------------------------------------------------------


def initialize(
    obj: Any,
    *,
    schemas: Iterable[str] | None = None,
    sqlite_attachments: Mapping[str, str] | None = None,
    tables: Iterable[Any] | None = None,
):
    if getattr(obj, "_ddl_executed", False):
        return

    ts = list(tables or [])
    if not ts:
        if hasattr(obj, "_collect_tables"):
            ts = list(obj._collect_tables())  # type: ignore[attr-defined]
        elif hasattr(obj, "__table__"):
            ts = [obj.__table__]  # type: ignore[attr-defined]

    kwargs: Dict[str, Any] = {}
    if hasattr(obj, "_collect_tables"):
        kwargs["router"] = obj
    elif hasattr(obj, "__table__"):
        kwargs["model"] = obj

    def _resolve_registered_model(name: str, registered: Any) -> Any:
        if isinstance(registered, type):
            return registered
        resolver = getattr(obj, "_resolve_registered_model", None)
        if callable(resolver):
            try:
                model = resolver(name, registered)
                if isinstance(model, type):
                    return model
            except Exception:
                pass
        return None

    provider_tables: Dict[int, tuple[Any, list[Any]]] = {}
    if (
        not tables
        and hasattr(obj, "tables")
        and isinstance(getattr(obj, "tables"), dict)
    ):
        for name, registered in getattr(obj, "tables").items():
            model = _resolve_registered_model(name, registered)
            if not isinstance(model, type):
                continue
            table = getattr(model, "__table__", None)
            if table is None or not getattr(table, "columns", None):
                continue
            table_provider = _resolver.resolve_provider(
                router=obj if hasattr(obj, "_collect_tables") else None,
                model=model,
            )
            if table_provider is None:
                continue
            key = id(table_provider)
            if key not in provider_tables:
                provider_tables[key] = (table_provider, [])
            bucket = provider_tables[key][1]
            if table not in bucket:
                bucket.append(table)

    prov = _resolver.resolve_provider(**kwargs)
    if prov is None and not provider_tables:
        raise ValueError("Engine provider is not configured")
    if prov is not None:
        key = id(prov)
        if key not in provider_tables:
            provider_tables[key] = (prov, [])
        if not provider_tables[key][1]:
            provider_tables[key][1].extend(ts)

    def _bootstrap(db, *, table_group: list[Any]):
        bind = db.get_bind() if hasattr(db, "get_bind") else db
        _create_all_on_bind(
            bind,
            schemas=schemas,
            sqlite_attachments=sqlite_attachments,
            tables=table_group,
        )

        # Keep ``obj.tables`` as a model registry. Runtime routing, docs generation,
        # and diagnostics all read that mapping expecting model classes, not
        # SQLAlchemy ``Table`` objects.

    def _close_without_loop(db):
        close = getattr(db, "close", None)
        if not callable(close):
            return
        out = close()
        if inspect.isawaitable(out):
            asyncio.run(out)

    def _close_with_loop(db):
        close = getattr(db, "close", None)
        if not callable(close):
            return None
        out = close()
        if inspect.isawaitable(out):
            loop = asyncio.get_running_loop()
            return loop.create_task(out)
        return None

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running event loop; fall back to fully synchronous bootstrap
        for provider, table_group in provider_tables.values():
            db = next(provider.get_db())
            try:
                _bootstrap(db, table_group=table_group)
            finally:
                _close_without_loop(db)
        setattr(obj, "_ddl_executed", True)
        return
    else:
        # If we're already inside an event loop but the provider is synchronous
        # (i.e. ``get_db`` is neither coroutine nor async generator), we can
        # bootstrap synchronously as well. This mirrors previous "initialize_sync"
        # behaviour and allows ``initialize()`` to be invoked without ``await``
        # from async contexts when using sync engines.
        if all(
            (not inspect.iscoroutinefunction(provider.get_db))
            and (not inspect.isasyncgenfunction(provider.get_db))
            for provider, _ in provider_tables.values()
        ):
            pending_closes = []
            for provider, table_group in provider_tables.values():
                db = next(provider.get_db())
                try:
                    _bootstrap(db, table_group=table_group)
                finally:
                    pending = _close_with_loop(db)
                    if pending is not None:
                        pending_closes.append(pending)
            setattr(obj, "_ddl_executed", True)

            class _Completed:
                def __init__(self, pending):
                    self._pending = tuple(pending or ())

                def __await__(self):  # pragma: no cover - trivial
                    if not self._pending:
                        if False:
                            yield None
                        return None

                    async def _wait_pending():
                        for pending in self._pending:
                            await pending
                        return None

                    return _wait_pending().__await__()

            return _Completed(pending_closes)

        async def _inner():
            for provider, table_group in provider_tables.values():
                if inspect.isasyncgenfunction(provider.get_db):
                    async for adb in provider.get_db():
                        await adb.run_sync(
                            lambda sync_db: _bootstrap(sync_db, table_group=table_group)
                        )
                        break
                    continue

                gen = provider.get_db()
                db = next(gen)
                try:
                    if hasattr(db, "run_sync"):
                        await db.run_sync(
                            lambda sync_db: _bootstrap(sync_db, table_group=table_group)
                        )
                    else:
                        bind = db.get_bind()
                        await asyncio.to_thread(
                            _create_all_on_bind,
                            bind,
                            schemas=schemas,
                            sqlite_attachments=sqlite_attachments,
                            tables=table_group,
                        )
                finally:
                    try:
                        next(gen)
                    except StopIteration:
                        pass
            setattr(obj, "_ddl_executed", True)

        return _inner()
