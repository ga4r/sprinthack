from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

from parser import BaseStation


class BuildType(str, Enum):
    hard = "плотная"
    medium = "средняя"
    light = "сельская"


BUILD_COEFF: Dict[BuildType, float] = {
    BuildType.hard: 1.21,
    BuildType.medium: 0.9,
    BuildType.light: 0.47,
}


@dataclass
class Zone:
    name: str
    area_km2: float
    build_type: BuildType
    base_stations: List[BaseStation]

    def build_coeff(self) -> float:
        return BUILD_COEFF[self.build_type]

    def r0_km(self) -> float:
        """
        R0= √(s/π), где s - площадь района обслуживания
        """
        return math.sqrt(self.area_km2 / math.pi)

    def l_for_station(self, st: BaseStation) -> float:
        """
        Число сот L можно определить по формуле:
        L=K*(R0 /R)2 ,  где R0 - радиус покрытия базовой станции, R - радиус покрытия базовой станции, К - коэффициент застройки
        """
        R0 = self.r0_km()
        R = st.radius_km()
        return self.build_coeff() * (R0 / R) ** 2

    def l_avg(self) -> float:
        """
        Обратите внимание, что при расчете количестве базовых станций по району значение L -среднее арифметическое по всем БС. 
        """
        if not self.base_stations:
            raise ValueError(f"Zone '{self.name}' has no base stations")
        values = [self.l_for_station(st) for st in self.base_stations]
        return sum(values) / len(values)

    def choose_cluster_stations(self) -> Tuple[BaseStation, BaseStation, BaseStation]:
        """
        Кластер состоит из С базовых станций, работающих в разных диапазонах частот. С - аддитивная (суммирующая) составляющая, равная:
         C = D1^(5/2) + D2^(3/2) + D3^(1/2), где D1, D2, D3- диаметры 3-х любых базовых станций с разной частотой, в порядке убывания, то есть - D1 - наибольший диаметр, D3 - наименьший диаметр. 

        Выбирает 3 БС для кластера:
        - с разными частотами;
        - сортировка с наибольшими диаметрами.
        """
        if len(self.base_stations) < 3:
            raise ValueError("Need at least 3 base stations to form a cluster")

        # сортируем по диаметру
        sorted_by_diameter = sorted(self.base_stations, key=lambda s: s.diameter_km(), reverse=True)

        chosen: List[BaseStation] = []
        used_freq: set[int] = set()

        for st in sorted_by_diameter:
            if st.frequency_hz in used_freq:
                continue
            chosen.append(st)
            used_freq.add(st.frequency_hz)
            if len(chosen) == 3:
                break

        if len(chosen) != 3:
            raise ValueError("Not enough stations with distinct frequencies for a cluster")

        return chosen[0], chosen[1], chosen[2]

    def cluster_c(self, stations: Optional[Sequence[BaseStation]] = None) -> float:
        """
        C = D1^(5/2) + D2^(3/2) + D3^(1/2), где D1>=D2>=D3.
        """
        if stations is None:
            stations = self.choose_cluster_stations()
        if len(stations) != 3:
            raise ValueError("stations must have length 3")

        diameters = sorted([st.diameter_km() for st in stations], reverse=True)
        d1, d2, d3 = diameters
        return (d1 ** (5 / 2)) + (d2 ** (3 / 2)) + (d3 ** (1 / 2))

    def n_stations(self, cluster_stations: Optional[Sequence[BaseStation]] = None) -> float:
        """
        n = L/C
        если is_handover_ok() is False то n = L/C * 1.4
        """
        L = self.l_avg()
        C = self.cluster_c(cluster_stations)
        n = L / C
        if self.is_handover_ok() is False:
            n *= 1.4
        return n
