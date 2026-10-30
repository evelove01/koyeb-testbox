#!/usr/bin/env bash
# ??????????????????
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "[1/4] apt update"
sudo apt-get update -y

echo "[2/4] ?? nginx + curl"
sudo apt-get install -y --no-install-recommends nginx curl

echo "[3/4] ?????"
sudo nginx -t
sudo systemctl enable --now nginx
curl -fsS -o /dev/null -w "nginx HTTP %{http_code}\n" http://127.0.0.1:80

echo "[4/4] ????"