#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-smartresolve.settings.production}"

npm ci
npm run build:css
python manage.py train_classifiers
python manage.py collectstatic --noinput
