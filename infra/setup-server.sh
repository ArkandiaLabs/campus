#!/usr/bin/env bash
# One-time setup script for a fresh Hetzner VPS (Ubuntu 24.04).
# Run as root: curl -sSL <this-url> | bash
# Or: ssh root@<server-ip> 'bash -s' < infra/setup-server.sh
set -euo pipefail

DEPLOY_USER="deploy"
REPO_URL="git@github.com:arkandia/campus.git"  # adjust if needed
APP_DIR="/home/${DEPLOY_USER}/campus"

echo "==> Installing Docker..."
apt-get update -qq
apt-get install -y -qq ca-certificates curl git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -qq
apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "==> Creating deploy user..."
id -u "$DEPLOY_USER" &>/dev/null || useradd -m -s /bin/bash "$DEPLOY_USER"
usermod -aG docker "$DEPLOY_USER"

echo "==> Setting up SSH key for deploy user..."
DEPLOY_HOME="/home/${DEPLOY_USER}"
mkdir -p "${DEPLOY_HOME}/.ssh"
# Copy root's authorized_keys so the same key works for the deploy user
if [ -f /root/.ssh/authorized_keys ]; then
  cp /root/.ssh/authorized_keys "${DEPLOY_HOME}/.ssh/authorized_keys"
fi
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${DEPLOY_HOME}/.ssh"
chmod 700 "${DEPLOY_HOME}/.ssh"
chmod 600 "${DEPLOY_HOME}/.ssh/authorized_keys" 2>/dev/null || true

echo "==> Cloning repository..."
sudo -u "$DEPLOY_USER" git clone "$REPO_URL" "$APP_DIR" || {
  echo "Clone failed — if the repo is private, add the deploy key first."
  echo "You can also manually clone as the deploy user later."
}

echo ""
echo "=========================================="
echo "  Server setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. SSH in as '${DEPLOY_USER}' and cd to ${APP_DIR}"
echo "  2. Copy .env.example to .env and fill in production values:"
echo "     cp .env.example .env && nano .env"
echo "  3. Start services:"
echo "     cd ${APP_DIR}/infra"
echo "     docker compose -f docker-compose.prod.yml up -d"
echo "  4. Run database migrations:"
echo "     docker compose -f docker-compose.prod.yml exec -T db psql -U postgres < ../database/schema/baseline.sql"
echo "     docker compose -f docker-compose.prod.yml exec -T db psql -U postgres < ../database/migrations/001_add_auth_user_id_to_core_client.sql"
echo "     docker compose -f docker-compose.prod.yml exec -T db psql -U postgres < ../database/migrations/002_create_ed_content.sql"
echo "     docker compose -f docker-compose.prod.yml exec -T db psql -U postgres < ../database/migrations/003_create_ed_content_progress.sql"
echo "     docker compose -f docker-compose.prod.yml exec -T db psql -U postgres < ../database/migrations/004_enable_rls_campus.sql"
echo "     docker compose -f docker-compose.prod.yml exec -T db psql -U postgres < ../database/migrations/005_drop_ed_content_progress.sql"
echo "  5. Seed data (optional):"
echo "     docker compose -f docker-compose.prod.yml exec -T db psql -U postgres < ../database/seeds/seed.sql"
echo ""
echo "  Add these GitHub repo secrets for automated deploys:"
echo "    DEPLOY_HOST     = $(curl -s ifconfig.me)"
echo "    DEPLOY_USER     = ${DEPLOY_USER}"
echo "    DEPLOY_SSH_KEY  = <private SSH key matching the deploy user's authorized_keys>"
