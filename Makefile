# AI Terminal — one-command workflows.
#   make up      start everything (rebuilds images only when needed)
#   make logs    follow logs
#   make seed    create demo user + sample data
#   make down    stop everything

.PHONY: up down logs ps seed front-deps clean

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

seed:
	docker compose exec backend python -m scripts.seed

# Run after adding an npm package: renews the node_modules volume,
# otherwise the container keeps the old one and new imports 500.
front-deps:
	docker compose up -d --build -V frontend

# Remove containers + images for this project (keeps DB data)
clean:
	docker compose down --rmi local
