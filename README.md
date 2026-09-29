# Shaarli Newsletter

Génère et envoie automatiquement chaque matin une newsletter reprenant les liens 
partagés la veille sur votre instance Shaarli, avec interface d'administration web.

## Fonctionnalités

- Interface admin (auth basique) pour configurer Shaarli, SMTP, planification
- 6 thèmes graphiques (couleurs + polices)
- Météo du jour (Open-Meteo, gratuit, sans clé API)
- Aperçu en direct de la newsletter
- Envoi manuel ou automatique (planificateur intégré)

## Installation

\`\`\`bash
git clone https://github.com/VOTRE_USER/shaarli-newsletter.git
cd shaarli-newsletter
cp .env.example .env
nano .env   # ADMIN_USER, ADMIN_PASSWORD, TZ

docker compose up -d --build
\`\`\`

Accédez ensuite à `http://votre-vps:8080/admin` (via reverse proxy HTTPS recommandé).

## Configuration Shaarli

Dans Shaarli : **Réglages > Configuration > API REST**, copiez le secret généré 
dans le champ correspondant de l'interface admin.