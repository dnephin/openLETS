#!/bin/bash


django="Django-1.3.1"

# TODO: check for django already installed
mkdir -p ./packages
cd packages
wget -O $django.tar.gz http://www.djangoproject.com/download/1.3.1/tarball/ 
tar -xzf $django.tar.gz
cd $django
python setup.py install

