#!/bin/bash

# Navigate to your docker-compose project directory (where your docker-compose.yml file is located)
cd /home/aaronrai24/projects/DollarDiscordBot

# Rebuild the Docker images
docker-compose up -d --build

# Prune dangling images (those not associated with containers)
docker image prune -f
