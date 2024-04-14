#!/bin/bash

test -d web || mkdir web
test -d build/spacedefense && rm -rf build/spacedefense
mkdir -p build/spacedefense/spacedefense/assets/images
mkdir -p build/spacedefense/spacedefense/assets/sounds

cp -r spacedefense/* build/spacedefense/spacedefense/

rm -f build/spacedefense/main.py
cp wasm.py build/spacedefense/main.py

rm -fr build/spacedefense/spacedefense/__pycache__

python -m pygbag --build build/spacedefense
python3 -m pygbag --archive build/spacedefense/main.py

cp build/spacedefense/build/web/index.html web/index.html
cp build/spacedefense/build/web/build/spacedefense.apk web/build/spacedefense.apk
cp build/spacedefense/build/web.zip web/web.zip
rm -fr build/spacedefense