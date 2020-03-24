#!/usr/bin/env bash
cd flaskr
rm dist/run
pyinstaller -w -F --add-data "templates:templates" --add-data "static:static" run.py