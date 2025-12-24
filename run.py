from parser import BaseStationParser
from zone import Zone, BuildType

stations = BaseStationParser.parse("Базовые станции.xlsx")

zone = Zone(
    name="Адмиралтейский",
    area_km2=250.0,
    build_type=BuildType.hard,
    base_stations=stations,
)

print("n =", zone.n_stations())
