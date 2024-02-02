#!/bin/bash

git pull origin main

cd "${0%/*}"
pip install pipreqs
pipreqs .
pip install -r requirements.txt
python3 generate_post.py

# git add .
# git commit -m "post: $(date '+%Y-%m-%d')"

# git push origin main