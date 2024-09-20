# Navigate to your docker-compose project directory and rebuild the Docker images
cd "B:\Personal Projects\DollarDiscordBot"

# Rebuild the Docker images
docker-compose up -d --build

# Prune dangling images (those not associated with containers)
docker image prune -f
