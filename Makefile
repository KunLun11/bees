.PHONY: help install dev test test-cov lint format migrate upgrade downgrade run run-dev clean

# Colors
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m

help:
	@echo "$(YELLOW)Доступные команды:$(NC)"
	@echo "  $(GREEN)install$(NC)      - Установить зависимости"
	@echo "  $(GREEN)dev$(NC)          - Установить dev-зависимости"
	@echo "  $(GREEN)test$(NC)         - Запустить тесты"
	@echo "  $(GREEN)test-cov$(NC)     - Запустить тесты с покрытием"
	@echo "  $(GREEN)lint$(NC)         - Проверить код линтером"
	@echo "  $(GREEN)format$(NC)       - Форматировать код"
	@echo "  $(GREEN)migrate$(NC)      - Создать миграцию (m=описание)"
	@echo "  $(GREEN)upgrade$(NC)      - Применить миграции"
	@echo "  $(GREEN)downgrade$(NC)    - Откатить миграцию"
	@echo "  $(GREEN)run$(NC)          - Запуск приложения (production)"
	@echo "  $(GREEN)run-dev$(NC)      - Запуск приложения (development)"
	@echo "  $(GREEN)clean$(NC)        - Очистка временных файлов"
	@echo "  $(GREEN)stop$(NC)         - Остановить приложение"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

lint:
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/
	isort src/ tests/

# Миграции
migrate:
	@if [ -z "$(m)" ]; then \
		echo "Использование: make migrate m=\"описание миграции\""; \
	else \
		cd src && alembic revision --autogenerate -m "$(m)"; \
	fi

upgrade:
	cd src && alembic upgrade head

downgrade:
	cd src && alembic downgrade -1

stop:
	@echo "Останавливаем сервер..."
	-pkill -f "granian.*src.main:app" 2>/dev/null || true
	-pkill -f "python" 2>/dev/null || true
	@sleep 1
	@echo "Сервер остановлен"

# Запуск приложения
run:
	granian \
		--host 0.0.0.0 \
		--port 8000 \
		--workers 4 \
		--loop asyncio \
		--interface asgi \
		src.main:app

run-dev:
	granian \
		--host 0.0.0.0 \
		--port 8000 \
		--workers 1 \
		--loop asyncio \
		--interface asgi \
		--reload \
		src.main:app

run-debug:
	uvicorn src.main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--reload \
		--log-level debug \
		--workers 1

kill-port:
	@echo "Убиваем процессы на порту 8000..."
	-$(shell kill -9 $$(lsof -t -i :8000) 2>/dev/null || true)
	@echo "Порт 8000 освобождён."

# Очистка
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	find . -name ".coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

# Деплой
deploy: clean
	@echo "Сборка для деплоя..."
	# Добавь команды деплоя здесь

# Docker
docker-build:
	docker build -t bees-app .

docker-run:
	docker run -p 8000:8000 --env-file .env bees-app

# Миграции в Docker
docker-migrate:
	docker-compose exec web alembic upgrade head

# База данных
db-shell:
	docker-compose exec db psql -U postgres bees_db

# Логи
logs:
	docker-compose logs -f

# Система
status:
	@echo "$(YELLOW)Статус приложения:$(NC)"
	@echo "  PID: $$(ps aux | grep granian | grep -v grep | awk '{print $$2}' | head -1)"
	@echo "  Порт: 8000"
	@echo "  База данных: $$(docker-compose ps db 2>/dev/null | grep Up || echo "Не запущена")"

# Инициализация проекта
init: install migrate upgrade
	@echo "$(GREEN)Проект инициализирован!$(NC)"
	@echo "Запустите: $(YELLOW)make run-dev$(NC)"