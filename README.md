### Установка

```bash
pip install -r requirements.txt
```

### Packages

- `pandas>=2.0.0` - Data manipulation and Excel file parsing
- `openpyxl>=3.1.0` - Excel file format support
- `requests>=2.31.0` - HTTP API integration
- `pytest>=7.4.0` - Testing framework (dev)
- `pytest-cov>=4.1.0` - Test coverage (dev)

## 🚀 Начало

```python
from parser import BaseStationParser
from zone import Zone, BuildType

# Парсим станции
stations = BaseStationParser.parse("Базовые станции.xlsx")

# Создаем зону
zone = Zone(
    name="Адмиралтейский",
    area_km2=250.0,
    build_type=BuildType.hard,
    base_stations=stations,
)

# Считаем Станции
n = zone.n_stations()
print(f"n Станций: {n}")
```

### Пример

```bash
python3 run.py
```
