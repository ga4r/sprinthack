from typing import Optional

import requests


class ApiHandoverProvider:
    def __init__(self):
        self.base_url = "http://192.168.0.100:100/api/basestation"

    def get_handover_avg(self, base_station_id: int) -> Optional[float]:
        try:
            url = f"{self.base_url}/{base_station_id}"
            r = requests.get(url, timeout=2)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return float(r.text.strip())
        except Exception:
            return 15.0
