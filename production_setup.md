# GabeGardener Production Setup Guide

This guide covers setting up GabeGardener in various production environments.

## Table of Contents
- [Pterodactyl Panel](#pterodactyl-panel)
- [Docker](#docker)
- [Raspberry Pi](#raspberry-pi)
- [Render](#render)
- [Heroku](#heroku)
- [AWS Lambda](#aws-lambda)
- [Google Cloud Run](#google-cloud-run)
- [Railway](#railway)
- [Fly.io](#flyio)
- [Replit](#replit)
- [Windows Service](#windows-service)
- [Linux Systemd](#linux-systemd)
- [Manual Installation](#manual-installation)

## Pterodactyl Panel

1. Create a new server using the GabeGardener egg
2. Configure the following variables:
   - `STEAM_USERNAME`: Your Steam account username
   - `STEAM_PASSWORD`: Your Steam account password
   - `STEAM_SHARED_SECRET`: (Optional) Your Steam shared secret for 2FA
   - `DASHBOARD_ENABLED`: Set to "true" to enable the web dashboard
   - `DASHBOARD_PORT`: Port for the web dashboard (default: 5000)
3. Start the server

## Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

2. Create a configuration directory:
   ```bash
   mkdir -p config
   ```

3. Run the quick start script to create your configuration:
   ```bash
   python quick_start.py
   ```

4. Start with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Access the dashboard at http://localhost:5000

## Raspberry Pi

1. Install Python 3 and pip:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. Run the quick start script:
   ```bash
   python3 quick_start.py
   ```

5. Create a systemd service for auto-start:
   ```bash
   sudo nano /etc/systemd/system/gabegardener.service
   ```

6. Add the following content:
   ```
   [Unit]
   Description=GabeGardener Steam Hour Booster
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/gabegardener
   ExecStart=/usr/bin/python3 /home/pi/gabegardener/main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

7. Enable and start the service:
   ```bash
   sudo systemctl enable gabegardener
   sudo systemctl start gabegardener
   ```

8. Access the dashboard at http://raspberry-pi-ip:5000

## Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. Add environment variables:
   - `GABEGARDENER_DASHBOARD`: true
   - `GABEGARDENER_DASHBOARD_PORT`: 10000 (Render assigns this port)
   - `PORT`: 10000 (Required by Render)
5. Deploy the service

## Heroku

1. Clone the repository:
   ```bash
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

2. Create a Heroku app:
   ```bash
   heroku create your-gabegardener-app
   ```

3. Create a `Procfile` in the root directory:
   ```
   web: python main.py
   ```

4. Set environment variables:
   ```bash
   heroku config:set GABEGARDENER_DASHBOARD=true
   heroku config:set GABEGARDENER_DASHBOARD_PORT=$PORT
   ```

5. Add your Steam account details:
   ```bash
   heroku config:set GABEGARDENER_CONFIG_JSON='{"accounts":[{"username":"your_username","password":"your_password","shared_secret":"your_secret","visible":true,"games":["GabeGardener",730,440,570]}]}'
   ```

6. Deploy to Heroku:
   ```bash
   git push heroku main
   ```

## AWS Lambda

1. Create a Lambda function with Python 3.9 runtime
2. Set up environment variables:
   - `GABEGARDENER_CONFIG_JSON`: JSON string with your configuration
   - `GABEGARDENER_DASHBOARD`: false (Lambda doesn't support web servers)

3. Create a `lambda_function.py` file:
   ```python
   import os
   import json
   import tempfile
   from main import main

   def lambda_handler(event, context):
       # Create temp config file
       config_json = os.environ.get('GABEGARDENER_CONFIG_JSON', '{}')
       with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
           f.write(config_json)
           os.environ['GABEGARDENER_CONFIG'] = f.name
       
       # Run GabeGardener
       try:
           main()
           return {"statusCode": 200, "body": "GabeGardener started successfully"}
       except Exception as e:
           return {"statusCode": 500, "body": f"Error: {str(e)}"}
   ```

4. Set up a CloudWatch Events rule to trigger the Lambda function periodically

## Google Cloud Run

1. Clone the repository:
   ```bash
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

2. Build and push the Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/your-project/gabegardener
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy gabegardener \
     --image gcr.io/your-project/gabegardener \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars="GABEGARDENER_DASHBOARD=true,GABEGARDENER_DASHBOARD_PORT=8080"
   ```

4. Set up a Cloud Scheduler job to keep the service running

## Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add environment variables:
   - `GABEGARDENER_DASHBOARD`: true
   - `GABEGARDENER_DASHBOARD_PORT`: $PORT
   - Add your Steam account details as needed
4. Deploy the application

## Fly.io

1. Install the Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

3. Create a `fly.toml` file:
   ```toml
   app = "gabegardener"
   
   [build]
     builder = "paketobuildpacks/builder:base"
   
   [env]
     GABEGARDENER_DASHBOARD = "true"
     GABEGARDENER_DASHBOARD_PORT = "8080"
   
   [http_service]
     internal_port = 8080
     force_https = true
   ```

4. Deploy to Fly.io:
   ```bash
   fly launch
   ```

5. Set secrets for your Steam accounts:
   ```bash
   fly secrets set GABEGARDENER_CONFIG_JSON='{"accounts":[...]}'
   ```

## Replit

1. Create a new Repl and select "Import from GitHub"
2. Enter your GabeGardener repository URL
3. Set environment variables in the Secrets tab:
   - `GABEGARDENER_DASHBOARD`: true
   - `GABEGARDENER_DASHBOARD_PORT`: 443
   - Add your Steam account details as needed
4. Create a `.replit` file:
   ```
   language = "python3"
   run = "python main.py"
   ```
5. Run the Repl

## Windows Service

1. Install Python 3 and pip
2. Clone the repository:
   ```
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install NSSM (Non-Sucking Service Manager):
   - Download from https://nssm.cc/download
   - Extract to a folder

5. Create a batch file `start_gabegardener.bat`:
   ```batch
   @echo off
   cd C:\path\to\gabegardener
   python main.py
   ```

6. Install as a service:
   ```
   nssm.exe install GabeGardener C:\path\to\start_gabegardener.bat
   ```

7. Start the service:
   ```
   nssm.exe start GabeGardener
   ```

## Linux Systemd

1. Install Python 3 and pip
2. Clone the repository:
   ```bash
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/gabegardener.service
   ```

5. Add the following content:
   ```
   [Unit]
   Description=GabeGardener Steam Hour Booster
   After=network.target

   [Service]
   User=shankyepdia
   WorkingDirectory=/path/to/gabegardener
   ExecStart=/usr/bin/python3 /path/to/gabegardener/main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. Enable and start the service:
   ```bash
   sudo systemctl enable gabegardener
   sudo systemctl start gabegardener
   ```

## Manual Installation

1. Install Python 3 and pip
2. Clone the repository:
   ```bash
   git clone https://github.com/shankyepdia/gabegardener.git
   cd gabegardener
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the quick start script:
   ```bash
   python quick_start.py
   ```

5. Start the application:
   ```bash
   python main.py
   ```

6. Access the dashboard at http://localhost:5000
