#!/bin/bash

log_error() {
    sed -i "1s/^/$(date '+%Y-%m-%d %H:%M:%S') - Error: $1\n/" /var/log/generate_post_today.log
	echo "----------------" >> /var/log/generate_post_today.log
    echo /var/log/generate_post_today.log >> /var/log/generate_post.log
}

send_mail() {
    cat /var/log/generate_post_today.log > log.txt
    echo "Post generation failed today ($(date '+%Y-%m-%d')). Please find the attachment for further information." | mail -s "Afromation Blog | $1" -A ./log.txt vishwa0403@gmail.com soried@gmail.com 2>> /var/log/send_mail.log
    echo "$(date '+%Y-%m-%d %H:%M:%S')" >> /var/log/send_mail.log
    echo "----------------" >> /var/log/send_mail.log
    rm log.txt
}

run_command() {
    "$@" 2> /var/log/generate_post_today.log
    if [ $? -ne 0 ]; then
        log_error "Failed to execute: $*"
        send_mail "Failed to execute: $*"
        exit 1
    fi
}

cd "${0%/*}"
run_command git pull origin main
run_command pip install pipreqs
run_command pipreqs . --force
run_command pip install -r requirements.txt
run_command python3 generate_post.py
cd ..
run_command quarto render
run_command cp _sites/* /var/www/afromation/public_html/
git add .
run_command git commit -m "post: $(date '+%Y-%m-%d')"
run_command git push origin main
echo "$(date '+%Y-%m-%d %H:%M:%S') - Script executed successfully." >> /var/log/generate_post.log 
echo "----------------" >> /var/log/generate_post_today.log
exit 0

