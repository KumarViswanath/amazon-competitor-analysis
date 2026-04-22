.PHONY: setup install run backend frontend dev clean help

# Default target
help:
	@echo "🚀 Amazon Competitor Analysis Platform"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup    - Install all dependencies"
	@echo "  make run      - Run both backend and frontend"
	@echo "  make backend  - Run only backend server"
	@echo "  make frontend - Run only frontend server"
	@echo "  make dev      - Run in development mode"
	@echo "  make clean    - Clean build files"
	@echo "  make help     - Show this help"
	@echo ""

# Install all dependencies
setup:
	@echo "📦 Installing backend dependencies..."
	uv sync
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Setup complete!"

# Alias for setup
install: setup

# Run both servers
run:
	@echo "🚀 Starting both servers..."
	@echo "🐍 Backend will run at: http://localhost:8000"
	@echo "⚛️  Frontend will run at: http://localhost:3000"
	@echo "📚 API docs at: http://localhost:8000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop both servers"
	@make -j2 backend frontend

# Run backend only
backend:
	@echo "🐍 Starting backend server..."
	uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run frontend only  
frontend:
	@echo "⚛️  Starting frontend server..."
	cd frontend && npm start

# Development mode with auto-restart
dev: run

# Clean build files
clean:
	@echo "🧹 Cleaning build files..."
	rm -rf frontend/build/
	rm -rf frontend/node_modules/.cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	@echo "✅ Cleaned!"