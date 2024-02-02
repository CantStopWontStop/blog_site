#!/bin/bash


cd "${0%/*}"

git pull origin main

pip install pipreqs
pipreqs .
pip install -r requirements.txt
python3 generate_post.py

git commit -am "post: $(date '+%Y-%m-%d')"

git push origin main
