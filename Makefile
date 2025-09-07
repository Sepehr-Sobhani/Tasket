.PHONY: help setup install-deps start-dev clean lint type-check db-check db-setup db-reset db-push

# Default target
help:
	@echo "🚀 Flowmate - Collaborative Agile Project Management"
	@echo ""
	@echo "Available commands:"
	@echo "  setup          - Complete project setup"
	@echo "  install-deps   - Install all dependencies"
	@echo "  start-dev      - Start development server"
	@echo "  clean          - Clean all build artifacts"
	@echo "  lint           - Run linting on all code"
	@echo "  type-check     - Run type checking on all code"
	@echo "  db-check       - Check PostgreSQL connection"
	@echo "  db-setup       - Setup PostgreSQL database"
	@echo "  db-reset       - Reset database (WARNING: destroys all data)"
	@echo "  db-push        - Push database schema changes"
	@echo ""
	@echo "Environment Configuration:"
	@echo "  - Development: NODE_ENV=development (default)"
	@echo "  - Production: NODE_ENV=production"
	@echo "  - OAuth: Configure GOOGLE_CLIENT_ID, GITHUB_CLIENT_ID, etc."
	@echo ""

# Complete project setup
setup: check-prereqs install-deps db-setup db-push
	@echo "🎉 Flowmate setup complete!"
	@echo ""
	@echo "📋 To start the application:"
	@echo "  make start-dev          # Start development server"
	@echo ""
	@echo "🌐 Application: http://localhost:3000"
	@echo ""
	@echo "🔧 Next steps:"
	@echo "  1. Configure OAuth providers in .env.local"
	@echo "  2. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
	@echo "  3. Add GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET"

# Install all dependencies
install-deps:
	@echo "⚛️  Setting up Flowmate..."
	@pnpm install
	@echo "🎨 Setting up ShadCN UI..."
	@if [ ! -f "components.json" ]; then \
		pnpm dlx shadcn@latest init --yes; \
	else \
		echo "✅ ShadCN UI already initialized"; \
	fi
	@echo "🎨 Adding ShadCN UI components..."
	@pnpm dlx shadcn@latest add button card input label tabs badge dialog dropdown-menu popover select separator sonner tooltip avatar form textarea checkbox radio-group switch progress alert alert-dialog calendar command context-menu hover-card navigation-menu pagination scroll-area sheet skeleton table --yes
	@echo "✅ Dependencies installed"

# Start development server
start-dev:
	@echo "🚀 Starting Flowmate development server..."
	@pnpm run dev

# Clean all build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf .next node_modules .pnpm-store
	@echo "✅ Build artifacts cleaned"

# Run linting on all code
lint:
	@echo "🔍 Linting code..."
	@pnpm run lint

# Run type checking on all code
type-check:
	@echo "🔍 Type checking code..."
	@pnpm run type-check

# Check if PostgreSQL is running
db-check:
	@echo "🔍 Checking PostgreSQL connection..."
	@if command -v psql >/dev/null 2>&1; then \
		echo "✅ PostgreSQL client found"; \
		echo "ℹ️  Make sure PostgreSQL is running and accessible"; \
	else \
		echo "❌ PostgreSQL client not found. Please install PostgreSQL"; \
		echo "   macOS: brew install postgresql"; \
		echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"; \
		echo "   Or use Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres"; \
	fi

# Setup PostgreSQL database
db-setup:
	@echo "🗄️  Setting up PostgreSQL database..."
	@if [ ! -f ".env.local" ]; then \
		if [ -f "env.example" ]; then \
			cp env.example .env.local; \
			echo "✅ .env.local file created from env.example"; \
			echo "⚠️  Please update DATABASE_URL in .env.local with your PostgreSQL credentials"; \
		else \
			echo "Creating .env.local file..."; \
			cat > .env.local << 'EOF';\
# pragma: allowlist secret
DATABASE_URL="postgresql://username:password@localhost:5432/flowmate_dev"\
NEXTAUTH_URL="http://localhost:3000"\
# pragma: allowlist secret
NEXTAUTH_SECRET="your-nextauth-secret-key"\
GOOGLE_CLIENT_ID=""\
GOOGLE_CLIENT_SECRET=""\
GITHUB_CLIENT_ID=""\
GITHUB_CLIENT_SECRET=""\
NEXT_PUBLIC_APP_NAME="Flowmate"\
NEXT_PUBLIC_APP_DESCRIPTION="Collaborative Agile Project Management"\
EOF\
			echo "✅ .env.local file created"; \
			echo "⚠️  Please update DATABASE_URL in .env.local with your PostgreSQL credentials"; \
		fi; \
	fi
	@echo "✅ Database setup complete"

# Reset database (WARNING: destroys all data)
db-reset:
	@echo "⚠️  WARNING: This will destroy all data in the database!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		pnpm run db:push --force-reset; \
		echo "✅ Database reset complete"; \
	else \
		echo "Database reset cancelled."; \
	fi

# Push database schema changes
db-push:
	@echo "🔄 Pushing database schema changes..."
	@pnpm run db:push
	@echo "✅ Database schema updated"

# Check prerequisites
check-prereqs:
	@echo "🔍 Checking prerequisites..."
	@if ! command -v node >/dev/null 2>&1; then \
		echo "❌ Node.js is not installed. Please install Node.js first."; \
		exit 1; \
	fi
	@if ! command -v pnpm >/dev/null 2>&1; then \
		echo "⚠️  pnpm is not installed. Installing pnpm..."; \
		npm install -g pnpm; \
		echo "✅ pnpm installed successfully"; \
	fi
	@echo "✅ All prerequisites are satisfied"