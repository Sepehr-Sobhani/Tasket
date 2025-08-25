.PHONY: help setup setup-backend setup-frontend install-deps install-backend install-frontend start-backend start-frontend start-dev clean clean-backend clean-frontend lint lint-backend lint-frontend type-check type-check-backend type-check-frontend db-setup db-reset db-migrate generate-types setup-pre-commit install-pre-commit pre-commit-all pre-commit-update

# Default target
help:
	@echo "🚀 Tasket - Collaborative Agile Project Management"
	@echo ""
	@echo "Available commands:"
	@echo "  setup          - Complete project setup (backend + frontend)"
	@echo "  setup-backend  - Setup backend only"
	@echo "  setup-frontend - Setup frontend only"
	@echo "  install-deps   - Install all dependencies"
	@echo "  start-backend  - Start backend server"
	@echo "  start-frontend - Start frontend development server"
	@echo "  start-dev      - Start both backend and frontend"
	@echo "  clean          - Clean all build artifacts"
	@echo "  lint           - Run linting on all code"
	@echo "  type-check     - Run type checking on all code"
	@echo "  db-setup       - Setup PostgreSQL database"
	@echo "  db-reset       - Reset database (WARNING: destroys all data)"
	@echo "  db-migrate     - Run database migrations"
	@echo "  generate-types - Generate TypeScript types from OpenAPI schema"
	@echo "  setup-pre-commit - Setup pre-commit hooks"
	@echo "  pre-commit-all - Run all pre-commit hooks on all files"
	@echo "  pre-commit-update - Update pre-commit hooks"
	@echo ""
	@echo "Environment Configuration:"
	@echo "  - Development: NODE_ENV=development (default)"
	@echo "  - Production: NODE_ENV=production"
	@echo "  - Override API URL: NEXT_PUBLIC_API_URL=your-url"
	@echo ""

# Complete project setup
setup: db-setup setup-backend setup-frontend setup-pre-commit
	@echo "🎉 Tasket setup complete!"
	@echo ""
	@echo "📋 To start the application:"
	@echo "  make start-dev          # Start both backend and frontend"
	@echo "  make start-backend      # Start backend only"
	@echo "  make start-frontend     # Start frontend only"
	@echo ""
	@echo "📚 API Documentation: http://localhost:8000/docs"
	@echo "🌐 Frontend: http://localhost:3000"

# Setup backend
setup-backend: install-backend
	@echo "✅ Backend setup complete"

# Setup frontend
setup-frontend: install-frontend
	@echo "✅ Frontend setup complete"

# Install all dependencies
install-deps: install-backend install-frontend

# Install backend dependencies
install-backend:
	@echo "🐍 Setting up backend..."
	@cd backend && uv venv
	@cd backend && uv pip install -e .
	@cd backend && uv pip install -e ".[dev]"
	@echo "✅ Backend dependencies installed"

# Install frontend dependencies
install-frontend:
	@echo "⚛️  Setting up frontend..."
	@cd frontend && npm install
	@echo "🎨 Setting up ShadCN UI..."
	@cd frontend && npx shadcn@latest init --yes
	@echo "🎨 Adding ShadCN UI components..."
	@cd frontend && npx shadcn@latest add button card input label tabs badge dialog dropdown-menu popover select separator toast tooltip avatar form textarea checkbox radio-group switch progress alert alert-dialog calendar command context-menu hover-card navigation-menu pagination scroll-area sheet skeleton table --yes
	@echo "🔧 Generating TypeScript types from OpenAPI..."
	@cd frontend && npm run generate-types
	@echo "✅ Frontend dependencies installed"

# Start backend server
start-backend:
	@echo "🚀 Starting backend server..."
	@cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend development server
start-frontend:
	@echo "🚀 Starting frontend development server..."
	@cd frontend && npm run dev

# Start both backend and frontend (requires tmux)
start-dev:
	@echo "🚀 Starting both backend and frontend..."
	@if command -v tmux >/dev/null 2>&1; then \
		tmux new-session -d -s tasket -c $(PWD) \; \
		split-window -h \; \
		send-keys -t 0 "cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" Enter \; \
		send-keys -t 1 "cd frontend && npm run dev" Enter \; \
		attach-session -t tasket; \
	else \
		echo "⚠️  tmux not found. Please install tmux or run backend and frontend in separate terminals:"; \
		echo "  Terminal 1: make start-backend"; \
		echo "  Terminal 2: make start-frontend"; \
	fi

# Clean all build artifacts
clean: clean-backend clean-frontend

# Clean backend
clean-backend:
	@echo "🧹 Cleaning backend..."
	@cd backend && rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	@echo "✅ Backend cleaned"

# Clean frontend
clean-frontend:
	@echo "🧹 Cleaning frontend..."
	@cd frontend && rm -rf .next node_modules
	@echo "✅ Frontend cleaned"

# Run linting on all code
lint: lint-backend lint-frontend

# Lint backend
lint-backend:
	@echo "🔍 Linting backend..."
	@cd backend && uv run ruff check .

# Lint frontend
lint-frontend:
	@echo "🔍 Linting frontend..."
	@cd frontend && npm run lint

# Run type checking on all code
type-check: type-check-backend type-check-frontend

# Type check backend
type-check-backend:
	@echo "🔍 Type checking backend..."
	@cd backend && uv run ty check .

# Type check frontend
type-check-frontend:
	@echo "🔍 Type checking frontend..."
	@cd frontend && npm run type-check

# Setup PostgreSQL database
db-setup:
	@echo "🗄️  Setting up PostgreSQL database..."
	@if command -v psql >/dev/null 2>&1; then \
		echo "Creating database user 'tasket'..."; \
		psql postgres -c "CREATE USER tasket WITH PASSWORD 'tasket';" 2>/dev/null || echo "User 'tasket' already exists"; \  # pragma: allowlist secret
		echo "Creating database 'tasket'..."; \
		psql postgres -c "CREATE DATABASE tasket OWNER tasket;" 2>/dev/null || echo "Database 'tasket' already exists"; \
		echo "✅ Database setup complete"; \
	else \
		echo "❌ PostgreSQL client (psql) not found. Please install PostgreSQL first."; \
		exit 1; \
	fi

# Reset database (WARNING: destroys all data)
db-reset:
	@echo "⚠️  WARNING: This will destroy all data in the tasket database!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		if command -v psql >/dev/null 2>&1; then \
			echo "Dropping database 'tasket'..."; \
			psql postgres -c "DROP DATABASE IF EXISTS tasket;"; \
			echo "Creating database 'tasket'..."; \
			psql postgres -c "CREATE DATABASE tasket OWNER tasket;"; \
			echo "✅ Database reset complete"; \
		else \
			echo "❌ PostgreSQL client (psql) not found."; \
			exit 1; \
		fi; \
	else \
		echo "Database reset cancelled."; \
	fi

# Run database migrations
db-migrate:
	@echo "🔄 Running database migrations..."
	@cd backend && uv run alembic upgrade head
	@echo "✅ Database migrations complete"

# Create environment files
env-files:
	@echo "📝 Creating environment files..."
	@if [ ! -f "backend/.env" ]; then \
		if [ -f "backend/env.example" ]; then \
			cp backend/env.example backend/.env; \
			echo "✅ Backend .env file created from env.example"; \
		else \
			echo "Creating backend .env file..."; \
			cat > backend/.env << 'EOF'; \
# Database\
DATABASE_URL=postgresql://tasket:tasket@localhost:5432/tasket\  # pragma: allowlist secret
\
# Security\
SECRET_KEY=your-secret-key-change-in-production\  # pragma: allowlist secret
ACCESS_TOKEN_EXPIRE_MINUTES=480\
\
# CORS\
ALLOWED_HOSTS=["http://localhost:3000", "http://127.0.0.1:3000"]\
\
# GitHub Integration (optional)\
GITHUB_CLIENT_ID=\
GITHUB_CLIENT_SECRET=\
\
# Redis\
REDIS_URL=redis://localhost:6379\
\
# Environment\
ENVIRONMENT=development\
DEBUG=true\
EOF\
			echo "✅ Backend .env file created"; \
		fi; \
	fi
	@if [ ! -f "frontend/.env.local" ]; then \
		if [ -f "frontend/env.example" ]; then \
			cp frontend/env.example frontend/.env.local; \
			echo "✅ Frontend .env.local file created from env.example"; \
		else \
			echo "Creating frontend .env.local file..."; \
			cat > frontend/.env.local << 'EOF';\
NEXT_PUBLIC_API_URL=http://localhost:8000\
EOF\
			echo "✅ Frontend .env.local file created"; \
		fi; \
	fi

# Check prerequisites
check-prereqs:
	@echo "🔍 Checking prerequisites..."
	@if ! command -v python3 >/dev/null 2>&1; then \
		echo "❌ Python 3 is not installed. Please install Python 3 first."; \
		exit 1; \
	fi
	@if ! command -v node >/dev/null 2>&1; then \
		echo "❌ Node.js is not installed. Please install Node.js first."; \
		exit 1; \
	fi
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "⚠️  uv is not installed. Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully"; \
	fi
	@echo "✅ All prerequisites are satisfied"

# Generate TypeScript types from OpenAPI schema
generate-types:
	@echo "🔧 Generating TypeScript types from OpenAPI schema..."
	@cd frontend && npm run generate-types
	@echo "✅ TypeScript types generated"

# Setup pre-commit hooks
setup-pre-commit: install-pre-commit
	@echo "🔧 Setting up pre-commit hooks..."
	@pre-commit install
	@pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks installed"

# Install pre-commit
install-pre-commit:
	@echo "📦 Installing pre-commit..."
	@if ! command -v pre-commit >/dev/null 2>&1; then \
		if command -v pip3 >/dev/null 2>&1; then \
			pip3 install pre-commit; \
		elif command -v pip >/dev/null 2>&1; then \
			pip install pre-commit; \
		elif command -v brew >/dev/null 2>&1; then \
			brew install pre-commit; \
		else \
			echo "❌ Error: No package manager found. Please install pre-commit manually:"; \
			echo "  pip3 install pre-commit  # or"; \
			echo "  brew install pre-commit  # or"; \
			echo "  curl -s https://pre-commit.com/install-local.py | python3 -"; \
			exit 1; \
		fi; \
	else \
		echo "✅ pre-commit already installed"; \
	fi

# Run all pre-commit hooks on all files
pre-commit-all:
	@echo "🔍 Running pre-commit hooks on all files..."
	@pre-commit run --all-files

# Update pre-commit hooks
pre-commit-update:
	@echo "🔄 Updating pre-commit hooks..."
	@pre-commit autoupdate
