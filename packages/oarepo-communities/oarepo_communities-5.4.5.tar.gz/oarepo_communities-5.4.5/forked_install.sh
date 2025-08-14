#!/bin/bash
set -e

# forked_install.sh <package_name>
version=$(pip list | grep "$1 " | sed 's/.* //')
pip install -U --force-reinstall --no-deps https://github.com/oarepo/$1/archive/oarepo-$version.zip
