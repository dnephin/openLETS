export DJANGO_SETTINGS_MODULE=openlets.settings
export PYTHONPATH=.
python openlets/core/jobs/resolve_balances.py $@
