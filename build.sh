#!/usr/bin/env bash
cd qt_version
pyinstaller -F --add-data "db:db" --add-data "ui:ui" --add-data "data:data" main.py
cd ..
rm -r compiled
mkdir compiled
cp -r qt_version/data compiled/data
cp -r qt_version/db compiled/db
cp -r qt_version/ui compiled/ui
cp -r qt_version/отчёты compiled/отчёты
mv qt_version/dist/main compiled
cp qt_version/Сопроводительная_записка.txt compiled
cp qt_version/main.py compiled