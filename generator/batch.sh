#!/bin/bash


cd "${0%/*}"

git pull origin main

pip install pipreqs
pipreqs . --force
pip install -r requirements.txt
python3 generate_post.py

cd ..
git add .
git commit -m "post: $(date '+%Y-%m-%d')"

git push origin main
