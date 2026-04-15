#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input --clear

# Reintentar migrate hasta 5 veces (por si Neon tarda en despertar)
echo "==> Ejecutando migraciones..."
for i in 1 2 3 4 5; do
    python manage.py migrate && break || {
        echo "==> Intento $i fallido, esperando 10 segundos..."
        sleep 10
    }
done