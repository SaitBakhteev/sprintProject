#!/bin/bash
set -e  # если упадет какая-либо строка, то скрипт остановится
python manage.py migrate --no-input  # миграции в БД без подтверждения за счет флага --no-input
echo "Миграции в БД осуществлены успешно"
exec "$@"  # Исполняет команду CMD из Dockerfile