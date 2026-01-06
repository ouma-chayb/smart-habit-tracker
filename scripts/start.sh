#!/bin/bash
set -e

cd /home/ec2-user/smart-habit-tracker

# Installer python si besoin
sudo yum install -y python3

# Créer venv si inexistant
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Tuer l'ancien serveur
pkill -f app.py || true

# Lancer Flask
nohup python app.py > app.log 2>&1 &
