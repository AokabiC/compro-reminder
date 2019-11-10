#!/bin/bash

echo "Build start..."
rm -rf dist
mkdir dist
cp -r src/* dist
pipenv lock -r > requirements.txt
pip install -r requirements.txt -t dist
cd dist
zip -r ../dist.zip *
cd ..
rm requirements.txt
echo "Done."