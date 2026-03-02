from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Tuple


@dataclass(frozen=True)
class SchemaIn:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]


@dataclass(frozen=True)
class SchemaOut:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]
    expose: Tuple[str, ...]


@dataclass(frozen=True)
class OpView:
    schema_in: SchemaIn
    schema_out: SchemaOut
    paired_index: Dict[str, Dict[str, object]]
    virtual_producers: Dict[str, Callable[[object, dict], object]]
    to_stored_transforms: Dict[str, Callable[[object, dict], object]]
    refresh_hints: Tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OpKey:
    proto: str
    selector: str


@dataclass(frozen=True, slots=True)
class OpMeta:
    model: type
    alias: str
    target: str


@dataclass(frozen=True, slots=True)
class KernelPlan:
    proto_indices: Mapping[str, Any] = field(default_factory=dict)
    opmeta: tuple[OpMeta, ...] = ()
    opkey_to_meta: Mapping[OpKey, int] = field(default_factory=dict)
    phase_chains: Mapping[int, Mapping[str, list[Callable[..., Any]]]] = field(
        default_factory=dict
    )

    # Backward-compat mapping access used by older tests/callers.
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class RestMatcher(dict[str, int]):
    """Method/path matcher that also preserves legacy dict-style selectors."""

    def __init__(self) -> None:
        super().__init__()
        self._compiled: list[tuple[str, re.Pattern[str], int]] = []

    @staticmethod
    def _compile_template(path_template: str) -> re.Pattern[str]:
        normalized = (path_template or "/").rstrip("/") or "/"

        def repl(match: re.Match[str]) -> str:
            name = match.group(1)
            return rf"(?P<{name}>[^/]+)"

        pattern_src = re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, normalized)
        if normalized != "/":
            pattern_src += "/?"
        return re.compile("^" + pattern_src + "$")

    def add(self, method: str, path_template: str, meta_index: int) -> None:
        key = f"{method.upper()} {path_template}"
        self[key] = meta_index
        pattern = self._compile_template(path_template)
        self._compiled.append((method.upper(), pattern, meta_index))

    def match(self, method: str, path: str) -> tuple[int, dict[str, str]]:
        method_u = method.upper()
        normalized = (path or "/").rstrip("/") or "/"

        exact_key = f"{method_u} {normalized}"
        if exact_key in self:
            return self[exact_key], {}

        for compiled_method, pattern, meta_index in self._compiled:
            if compiled_method != method_u:
                continue
            matched = pattern.match(normalized)
            if matched:
                return meta_index, {k: v for k, v in matched.groupdict().items()}
        raise KeyError(f"{method_u} {path}")

    __call__ = match
