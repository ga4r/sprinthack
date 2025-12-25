from dataclasses import dataclass, asdict
from typing import Any, Optional, Tuple

import math
import pandas as pd

from handover import ApiHandoverProvider


@dataclass
class BaseStation:
    base_station_id: int
    base_station_name: str
    coverage_area_sq_km: float
    frequency_hz: int
    antenna_type: str
    handover_min: Optional[float]
    handover_max: Optional[float]
    handover_avg: Optional[float]
    standard: str
    installation_coordinates: str = ""

    def is_handover_ok(self) -> Optional[bool]:
        if self.handover_avg is None or self.handover_min is None or self.handover_max is None:
            return None
        return self.handover_min <= self.handover_avg <= self.handover_max

    def radius_km(self) -> float:
        return math.sqrt(self.coverage_area_sq_km / math.pi)

    def diameter_km(self) -> float:
        return 2.0 * self.radius_km()


class BaseStationParser:
    COL_ID = "ИД базовой станции"
    COL_NAME = "Название БС"
    COL_COVERAGE = "Площадь зоны покрытия, кв.км"
    COL_FREQ = "Частота,Гц"
    COL_ANT = "Тип антенны"
    COL_HANDOVER = "Диапазон показателей хэндовера"
    COL_STD = "Стандарт"
    COL_COORDS = "Координаты установки"

    @staticmethod
    def parse_handover_range(text: Any) -> Optional[Tuple[float, float]]:
        if text is None or (isinstance(text, float) and pd.isna(text)):
            return None
        s = str(text).strip().lower()
        if not s:
            return None

        s = s.replace(" ", "")
        s = s.replace("от", "")
        s = s.replace("до", "-")

        if "-" not in s:
            return None

        parts = s.split("-")
        if len(parts) != 2:
            return None

        try:
            mn = float(parts[0].replace(",", "."))
            mx = float(parts[1].replace(",", "."))
            return (mn, mx)
        except ValueError:
            return None

    @classmethod
    def parse(cls, path: str, *, sheet_name: int | str = 0) -> list[BaseStation]:
        df = pd.read_excel(path, sheet_name=sheet_name)

        required = [
            cls.COL_ID, cls.COL_NAME, cls.COL_COVERAGE, cls.COL_FREQ,
            cls.COL_ANT, cls.COL_HANDOVER, cls.COL_STD, cls.COL_COORDS
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}. Present: {list(df.columns)}")

        api = ApiHandoverProvider()
        items: list[BaseStation] = []

        for _, r in df.iterrows():
            hr = cls.parse_handover_range(r[cls.COL_HANDOVER])
            hand_min = hr[0] if hr else None
            hand_max = hr[1] if hr else None

            coverage = r[cls.COL_COVERAGE]
            coverage_f = 0.0 if pd.isna(coverage) else float(coverage)

            bs_id = int(r[cls.COL_ID])

            items.append(
                BaseStation(
                    base_station_id=bs_id,
                    base_station_name=str(r[cls.COL_NAME]).strip(),
                    coverage_area_sq_km=coverage_f,
                    frequency_hz=int(r[cls.COL_FREQ]),
                    antenna_type=str(r[cls.COL_ANT]).strip(),
                    handover_min=hand_min,
                    handover_max=hand_max,
                    handover_avg=api.get_handover_avg(bs_id),
                    standard=str(r[cls.COL_STD]).strip(),
                    installation_coordinates="" if pd.isna(r[cls.COL_COORDS]) else str(r[cls.COL_COORDS]).strip(),
                )
            )

        return items
