.PHONY: init dev prod status clean build switch-to-prod switch-to-dev

# Initialize uv project (run once)
init:
	@echo "🚀 Initializing uv project..."
	uv sync
	@echo "✅ Setup complete"

# Development mode (with local containers)
dev:
	@echo "🚀 Starting DEVELOPMENT mode (local containers)"
	COMPOSE_PROFILES=local docker-compose up -d
	@echo "✅ Services started:"
	@echo "  Neo4j Browser: http://localhost:7474 (neo4j/password)"
	@echo "  Qdrant: http://localhost:6333"
	@echo "  Redis: localhost:6379"
	@echo "  API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

# Production mode (API only, hosted services)
prod:
	@echo "🚀 Starting PRODUCTION mode (hosted services)"
	docker-compose up -d api
	@echo "✅ API started: http://localhost:8000"
	@echo "💡 Using environment variables from .env"

# Switch to production configuration  
switch-to-prod:
	@echo "🔄 Switching to PRODUCTION configuration..."
	@echo "# Production configuration" > .env
	@echo "ENVIRONMENT=production" >> .env
	@echo "LOG_LEVEL=INFO" >> .env
	@echo "" >> .env
	@echo "# Update these with your hosted service URLs:" >> .env
	@echo "NEO4J_URL=neo4j+s://your-instance.databases.neo4j.io" >> .env
	@echo "NEO4J_USERNAME=neo4j" >> .env
	@echo "NEO4J_PASSWORD=your-secure-password" >> .env
	@echo "" >> .env
	@echo "QDRANT_URL=https://your-cluster.qdrant.tech" >> .env
	@echo "QDRANT_API_KEY=your-api-key" >> .env
	@echo "" >> .env
	@echo "REDIS_URL=redis://username:password@your-redis-host:port" >> .env
	@echo "✅ Created production .env file"
	@echo "💡 Edit .env with your actual hosted service URLs, then run: make prod"

# Switch to development configuration
switch-to-dev:
	@echo "🔄 Switching to DEVELOPMENT configuration..."
	@echo "# Development configuration" > .env
	@echo "ENVIRONMENT=development" >> .env
	@echo "LOG_LEVEL=DEBUG" >> .env
	@echo "✅ Created development .env file"
	@echo "💡 Now run: make dev"

# Run locally with uv (no Docker)
run:
	@echo "🏃 Running locally with uv..."
	. .venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Build optimized image
build:
	@echo "🔨 Building Docker image..."
	docker build -t neo4j-graphrag-api:latest .
	@echo "📊 Image size:"
	@docker images neo4j-graphrag-api:latest

# Check status and health
status:
	@echo "📊 Current Docker services:"
	@docker-compose ps
	@echo ""
	@echo "🔍 API Health check:"
	@curl -s http://localhost:8000/health 2>/dev/null | jq . || echo "API not responding"
	@echo ""
	@echo "⚙️  Configuration:"
	@curl -s http://localhost:8000/config 2>/dev/null | jq . || echo "API not responding"

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Cleanup complete"

# Show help
help:
	@echo "🚀 Neo4j GraphRAG API Commands (LATEST Docker Images):"
	@echo ""
	@echo "🐍 Python: 3.13.5-alpine | 📊 Neo4j: 2025.05.0 | 🔍 Qdrant: v1.14.1 | 📦 Redis: 8-alpine"
	@echo ""
	@echo "💡 Optional: Use Python 3.14.0b3-alpine for bleeding edge (change Dockerfile)"
	@echo ""
	@echo "Setup:"
	@echo "  make init          Initialize project dependencies and install package"
	@echo "  make build         Build Docker image"
	@echo ""
	@echo "Development:"
	@echo "  make dev           Start local containers (Neo4j + Qdrant + Redis + API)"
	@echo "  make run           Run API locally with uv (no Docker)"
	@echo ""
	@echo "Production:"
	@echo "  make switch-to-prod   Create production .env template"
	@echo "  make prod            Start production API (hosted databases)"
	@echo "  make switch-to-dev   Create development .env"
	@echo ""
	@echo "Package Management:"
	@echo "  uv add <package>      Add new dependency"
	@echo "  uv remove <package>   Remove dependency"
	@echo "  uv sync              Sync dependencies"
	@echo ""
	@echo "Utilities:"
	@echo "  make status        Check service status and health"
	@echo "  make clean         Stop and remove all containers"
	@echo "  make help          Show this help"