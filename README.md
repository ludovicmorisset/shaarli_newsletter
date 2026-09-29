# Shaarli Newsletter

Génère et envoie chaque matin une newsletter avec les liens partagés la veille sur votre instance Shaarli. L’interface d’administration permet de configurer la source, l’envoi, la planification et l’apparence.

## Fonctionnalités

- Interface d’administration avec page de connexion et session sécurisée
- Six thèmes graphiques pour la newsletter
- Météo du jour via Open-Meteo, sans clé API
- Aperçu de la newsletter et envoi manuel
- Envoi automatique avec planificateur intégré

## Installation

```bash
git clone https://github.com/VOTRE_USER/shaarli-newsletter.git
cd shaarli-newsletter
cp env.example .env
```

Dans `.env`, définissez `ADMIN_USER`, un `ADMIN_PASSWORD` robuste et une clé aléatoire pour `SESSION_SECRET` (par exemple `openssl rand -hex 32`). Pour une connexion via HTTPS, définissez également `SESSION_COOKIE_SECURE=true`.

```bash
docker compose up -d --build
```

Ouvrez `http://votre-vps:8080/login` ou configurez un reverse proxy HTTPS avant d’exposer l’application à Internet.

## Configuration Shaarli

Dans Shaarli, ouvrez **Réglages > Configuration > API REST**, copiez le secret généré et renseignez-le dans l’interface d’administration.