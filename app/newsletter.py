from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from themes import THEMES
from shaarli_client import get_yesterday_links
from weather import get_weather

env = Environment(loader=FileSystemLoader("templates"))


def build_newsletter_html(settings) -> tuple[str, list[dict], datetime]:
    yesterday = datetime.now() - timedelta(days=1)

    exclude_tags = [t.strip() for t in settings.exclude_tags.split(",") if t.strip()]
    links = []
    if settings.shaarli_url and settings.shaarli_api_secret:
        links = get_yesterday_links(settings.shaarli_url, settings.shaarli_api_secret, exclude_tags)

    weather = None
    if settings.weather_enabled and settings.weather_lat and settings.weather_lon:
        try:
            weather = get_weather(settings.weather_lat, settings.weather_lon)
        except Exception:
            weather = None

    theme = THEMES.get(settings.theme, THEMES["journal"])

    template = env.get_template("newsletter.html")
    html = template.render(
        theme=theme,
        links=links,
        date=yesterday,
        show_descriptions=settings.show_descriptions,
        weather=weather,
        weather_label=settings.weather_label,
    )
    return html, links, yesterday