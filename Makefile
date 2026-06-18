.DEFAULT_GOAL := help

BACKEND_DIR := backend

# ─────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show all available commands
	@echo ""
	@echo "  Music Mood Therapy — Available Commands"
	@echo "  ──────────────────────────────────────────"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ─────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────

.PHONY: install
install: ## Install all backend Python dependencies via uv
	cd $(BACKEND_DIR) && uv sync

# ─────────────────────────────────────────────────────────────
# Data pipeline (run once before first use)
# ─────────────────────────────────────────────────────────────

.PHONY: label
label: ## Step 1 — label 114k songs with emotions → dataset_labeled.csv
	cd $(BACKEND_DIR) && uv run python src/label_emotions.py

.PHONY: train
train: label ## Step 2 — train RF + MLP models → .pkl files (also runs label)
	cd $(BACKEND_DIR) && uv run python src/train_classifier.py

# ─────────────────────────────────────────────────────────────
# Run the app
# ─────────────────────────────────────────────────────────────

.PHONY: run
run: ## Run the CLI conversation app (models must exist — run 'make train' first)
	cd $(BACKEND_DIR) && uv run python src/pipeline.py

.PHONY: start
start: ## Smart start — trains models if missing, then runs the app
	@if [ ! -f $(BACKEND_DIR)/models/emotion_classifier_rf.pkl ]; then \
		echo ""; \
		echo "  First run detected — setting up models..."; \
		echo "  This takes ~60 seconds and only happens once."; \
		echo ""; \
		$(MAKE) train; \
	fi
	$(MAKE) run

# ─────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────

.PHONY: demo
demo: ## Run librosa audio demo — usage: make demo FILE=path/to/song.mp3
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make demo FILE=path/to/song.mp3"; \
		exit 1; \
	fi
	cd $(BACKEND_DIR) && uv run python demo/librosa_demo.py $(FILE)

# ─────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────

.PHONY: docker-build
docker-build: ## Build all Docker containers
	docker-compose build

.PHONY: docker-run
docker-run: ## Run backend CLI in Docker (interactive)
	docker-compose run --rm backend

.PHONY: docker-up
docker-up: ## Start all services (backend + frontend) in Docker
	docker-compose up

# ─────────────────────────────────────────────────────────────
# Maintenance
# ─────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove all generated data and model files (forces full retrain)
	@echo "Removing generated files..."
	@rm -f $(BACKEND_DIR)/data/processed/dataset_labeled.csv
	@rm -f $(BACKEND_DIR)/models/*.pkl
	@echo "Done. Run 'make train' to regenerate."
