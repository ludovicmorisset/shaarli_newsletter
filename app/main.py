import os
import secrets
from datetime import datetime

from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from jinja2 import Environment, FileSystemLoader
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from settings import Settings, load_settings, save_settings, load_last_run, save_last_run
from themes import THEMES
from newsletter import build_newsletter_html
from mailer import send_email
from weather import geocode_city

app = FastAPI(title="Shaarli Newsletter")
env = Environment(loader=FileSystemLoader("templates"))
security = HTTPBasic()

scheduler = BackgroundScheduler()
scheduler.start()
current_job_id = "newsletter_job"


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    admin_user = os.environ.get("ADMIN_USER", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")
    correct_user = secrets.compare_digest(credentials.username, admin_user)
    correct_pass = secrets.compare_digest(credentials.password, admin_password)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    return True


def run_newsletter_job():
    settings = load_settings()
    now_str = datetime.now().isoformat(timespec="seconds")
    try:
        html, links, yesterday = build_newsletter_html(settings)
        if not links and not settings.send_if_empty:
            save_last_run(True, "Aucun lien hier, envoi ignoré.", now_str)
            return
        subject = f"{settings.subject_prefix} {yesterday.strftime('%d/%m/%Y')}"
        send_email(settings, subject, html)
        save_last_run(True, f"Newsletter envoyée ({len(links)} lien(s)).", now_str)
    except Exception as e:
        save_last_run(False, f"Erreur : {e}", now_str)


def reschedule(settings: Settings):
    try:
        scheduler.remove_job(current_job_id)
    except Exception:
        pass
    if settings.enabled and settings.send_time:
        hour, minute = settings.send_time.split(":")
        scheduler.add_job(
            run_newsletter_job,
            CronTrigger(hour=int(hour), minute=int(minute), timezone=settings.timezone),
            id=current_job_id,
            replace_existing=True,
        )


@app.on_event("startup")
def startup():
    settings = load_settings()
    reschedule(settings)


@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse("/admin")


@app.get("/admin", response_class=HTMLResponse)
def admin_page(auth: bool = Depends(check_auth)):
    settings = load_settings()
    last_run = load_last_run()
    job = scheduler.get_job(current_job_id)
    next_run = job.next_run_time.strftime("%d/%m/%Y %H:%M") if job else "désactivé"

    template = env.get_template("admin.html")
    return template.render(
        s=settings,
        themes=THEMES,
        last_run=last_run,
        next_run=next_run,
    )


@app.post("/admin", response_class=HTMLResponse)
def admin_save(
    request: Request,
    auth: bool = Depends(check_auth),
    shaarli_url: str = Form(""),
    shaarli_api_secret: str = Form(""),
    exclude_tags: str = Form(""),
    show_descriptions: bool = Form(False),
    send_if_empty: bool = Form(False),
    smtp_host: str = Form(""),
    smtp_port: int = Form(587),
    smtp_user: str = Form(""),
    smtp_password: str = Form(""),
    smtp_use_tls: bool = Form(False),
    mail_from: str = Form(""),
    mail_to: str = Form(""),
    subject_prefix: str = Form("📰 Ma veille du"),
    send_time: str = Form("07:00"),
    timezone: str = Form("Europe/Paris"),
    enabled: bool = Form(False),
    theme: str = Form("journal"),
    weather_enabled: bool = Form(False),
    weather_city: str = Form(""),
):
    old = load_settings()

    weather_label = old.weather_label
    weather_lat = old.weather_lat
    weather_lon = old.weather_lon

    if weather_city.strip() and weather_city.strip() != old.weather_city.strip():
        geo = geocode_city(weather_city)
        if geo:
            weather_label = geo["label"]
            weather_lat = geo["lat"]
            weather_lon = geo["lon"]
        else:
            weather_label = ""
            weather_lat = None
            weather_lon = None

    new_settings = Settings(
        shaarli_url=shaarli_url,
        shaarli_api_secret=shaarli_api_secret,
        exclude_tags=exclude_tags,
        show_descriptions=show_descriptions,
        send_if_empty=send_if_empty,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password or old.smtp_password,
        smtp_use_tls=smtp_use_tls,
        mail_from=mail_from,
        mail_to=mail_to,
        subject_prefix=subject_prefix,
        send_time=send_time,
        timezone=timezone,
        enabled=enabled,
        theme=theme,
        weather_enabled=weather_enabled,
        weather_city=weather_city,
        weather_label=weather_label,
        weather_lat=weather_lat,
        weather_lon=weather_lon,
    )
    save_settings(new_settings)
    reschedule(new_settings)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/send", response_class=HTMLResponse)
def admin_send_now(auth: bool = Depends(check_auth)):
    run_newsletter_job()
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/preview", response_class=HTMLResponse)
def admin_preview(theme: str = "journal", auth: bool = Depends(check_auth)):
    settings = load_settings()
    settings.theme = theme
    html, _, _ = build_newsletter_html(settings)
    return html