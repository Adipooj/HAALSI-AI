from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import json
from pathlib import Path


@dataclass
class SchemaArtifact:
    feature_columns: list[str] = field(default_factory=list)
    feature_defaults: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "feature_columns": self.feature_columns,
            "feature_defaults": self.feature_defaults,
            "metadata": self.metadata,
        }

        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SchemaArtifact":
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))

        return cls(
            feature_columns=data.get("feature_columns", []),
            feature_defaults=data.get("feature_defaults", {}),
            metadata=data.get("metadata", {}),
        )