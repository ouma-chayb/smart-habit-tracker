#!/bin/bash

cd /home/ec2-user/smart-habit-tracker

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

nohup python3 app.py > app.log 2>&1 &
