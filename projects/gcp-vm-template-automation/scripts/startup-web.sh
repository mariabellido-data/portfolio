#!/usr/bin/env bash
set -euxo pipefail

# Install Nginx and enable as an auto-start systemd service
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nginx

# Create a minimal landing page with hostname info
HOST="$(hostname)"
cat >/var/www/html/index.html <<EOF
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>GCP Web</title>
  </head>
  <body style="font-family: system-ui, Arial, sans-serif; margin: 40px;">
    <h1>It works</h1>
    <p>This page is served by <strong>$HOST</strong>.</p>
  </body>
</html>
EOF

# Ensure Nginx is enabled and started
systemctl enable nginx
systemctl restart nginx
