import httpx


def geocode_city(city: str) -> dict | None:
    """Retourne {label, lat, lon} pour une ville donnée, via Open-Meteo Geocoding."""
    if not city.strip():
        return None
    with httpx.Client(timeout=10) as client:
        resp = client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "fr"},
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results")
        if not results:
            return None
        r = results[0]
        label = r["name"]
        if r.get("admin1"):
            label += f", {r['admin1']}"
        if r.get("country"):
            label += f" ({r['country']})"
        return {"label": label, "lat": r["latitude"], "lon": r["longitude"]}


WEATHER_ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    71: "🌨️", 73: "🌨️", 75: "❄️",
    80: "🌦️", 81: "🌧️", 82: "⛈️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}


def get_weather(lat: float, lon: float) -> dict | None:
    with httpx.Client(timeout=10) as client:
        resp = client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                "timezone": "auto",
                "forecast_days": 1,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        daily = data.get("daily")
        if not daily:
            return None
        code = daily["weathercode"][0]
        return {
            "tmax": round(daily["temperature_2m_max"][0]),
            "tmin": round(daily["temperature_2m_min"][0]),
            "icon": WEATHER_ICONS.get(code, "🌡️"),
            "code": code,
        }