#!/bin/bash
# Should be run from the django project root.

python core/testing/build_model_fixtures.py
./manage.py dumpdata auth core > ./core/fixtures/testing/base.json
