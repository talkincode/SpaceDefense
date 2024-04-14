#!/bin/bash

test -d web || mkdir web
test -d spacedefense_wasm && rm -rf spacedefense_wasm
mkdir -p spacedefense_wasm/spacedefense/assets/images
mkdir -p spacedefense_wasm/spacedefense/assets/sounds

cp -r spacedefense/* spacedefense_wasm/spacedefense/

rm -f spacedefense_wasm/main.py
cp main.py spacedefense_wasm/main.py

rm -fr spacedefense_wasm/spacedefense/__pycache__

python -m pygbag --build spacedefense_wasm
python3 -m pygbag --archive spacedefense_wasm/main.py

cp web/index.html web/index.html
cp spacedefense_wasm/build/web/spacedefense_wasm.apk web/spacedefense_wasm.apk
cp spacedefense_wasm/build/web.zip web/web.zip
rm -fr spacedefense_wasm