"""Dataset construction utilities compatible with Qlib."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover - qlib optional
    from qlib.data import D  # type: ignore
    from qlib.contrib.data.handler import Alpha360  # type: ignore
except Exception:  # pragma: no cover
    D = None
    Alpha360 = None

from ..config import DataConfig


@dataclass
class DatasetBuilder:
    data_config: DataConfig
    handler_cls: Optional[type] = None

    def build(self):  # type: ignore[override]
        """Return a Qlib dataset instance."""

        if D is None or Alpha360 is None:
            raise RuntimeError(
                "Qlib is required to build datasets. Install microsoft/qlib and ensure "
                "the data bundle is available."
            )

        handler_class = self.handler_cls or Alpha360
        handler = handler_class(
            instruments=self.data_config.instruments,
            start_time=self.data_config.start_time,
            end_time=self.data_config.end_time,
        )

        return D.dataset(handler)
