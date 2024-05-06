#!/bin/bash

log_error() {
    echo "Error: $1" >&2
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Error: $1" >> /var/log/generate_post.log 
}

cd "${0%/*}" 

git pull origin main || { log_error "Failed to pull latest changes from Git."; exit 1; }

pip install pipreqs 

pipreqs . --force || { log_error "Failed to generate requirements.txt."; exit 1; }

pip install -r requirements.txt || { log_error "Failed to install dependencies from requirements.txt."; exit 1; }

python3 generate_post.py || { log_error "Failed to generate post using generate_post.py."; exit 1; }

cd .. 

git add .

git commit -m "post: $(date '+%Y-%m-%d')"

git push origin main || { log_error "Failed to push changes to remote repository."; exit 1; }

echo "$(date '+%Y-%m-%d %H:%M:%S') - Script executed successfully." >> /var/log/generate_post.log 


