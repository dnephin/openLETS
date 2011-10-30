#!/bin/bash
# Should be run from the django project root.

./manage.py dumpdata auth core > ./core/fixtures/testing/base.json
