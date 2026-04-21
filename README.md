# 🎯 WorkMate

## *Modern Service Marketplace API*

**Built with FastAPI • Hexagonal Architecture • Production-Ready**

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0+-dc382d.svg)](https://redis.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-api-documentation) •
[Development](#-development-workflow) • [Contributing](#-contributing)

---

## ✨ Features

## 🏗️ **Architecture**

- ⚡ **FastAPI** with automatic OpenAPI docs
- 🏛️ **Hexagonal Architecture** for clean separation
- 🎯 **Domain-Driven Design** principles
- 🧩 **Dependency Injection** for testability

## 🔧 **Infrastructure**

- 🐘 **PostgreSQL** with async SQLAlchemy
- ⚡ **Redis** for caching & sessions
- 📦 **Alembic** for database migrations
- 🐳 **Docker Compose** for easy setup

## 🧪 **Quality Assurance**

- ✅ Comprehensive test coverage
- 🔍 **MyPy** for static type checking
- 🎨 **Black** & **Ruff** for formatting
- 🪝 **Pre-commit** hooks

## 📊 **Developer Experience**

- 📝 Structured logging
- ⚙️ **Pydantic Settings** for config
- 🛠️ **Task** for easy commands
- 📚 Complete API documentation

---

## 📂 Project Structure

```text
workmate/
│
├── 📁 src/workmate/
│   ├── 🎯 domain/              # Core business logic & entities
│   ├── 🔄 application/         # Use cases & orchestration
│   ├── 🏗️ infrastructure/      # DB, repositories, config
│   ├── 🌐 presentation/        # API endpoints & web layer
│   └── 🚀 main.py             # Application entry point
│
├── 🧪 tests/                   # Unit, integration & e2e tests
├── 📦 alembic/                 # Database migration scripts
├── 🐳 docker-compose.yml       # Development environment
├── 🐋 Dockerfile              # Production container image
├── ⚙️ Taskfile.yml            # Development commands
└── 📖 README.md               # You are here!
```

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- 🐍 **Python 3.13+**
- 📦 **uv** (dependency management)
- 🐳 **Docker & Docker Compose**
- 🛠️ **Task** (task runner)

### ⚡ Option 1: One-Command Setup (Recommended)

```bash
task setup
```

**What this does:**

1. ✅ Creates `.env` file from example
2. 🏗️ Builds Docker images
3. 🚀 Starts PostgreSQL, Redis, and API
4. 📦 Applies database migrations
5. 🌐 Makes API available at `http://localhost:8000`

### 🔧 Option 2: Manual Setup

```bash
# 1️⃣ Clone the repository
git clone <your-repo-url>
cd workmate

# 2️⃣ Install dependencies
task install-dev

# 3️⃣ Configure environment
task env
# Edit .env with your credentials

# 4️⃣ Start services
task docker-up

# 5️⃣ Run migrations
task db-upgrade
```

---

## 🎯 Development Workflow

### Daily Commands

```bash
task dev                # 🔥 Start dev server with hot reload
task test               # 🧪 Run all tests
task format             # 🎨 Format code with Black & Ruff
task lint               # 🔍 Lint code
task typecheck          # 📝 Type checking with MyPy
```

### Testing

```bash
task test               # Run all tests
task test-unit          # Run unit tests only
task test-integration   # Run integration tests
task test-e2e           # Run end-to-end tests
task test-cov           # Run tests with coverage report
```

### Code Quality

```bash
task format             # Auto-format code
task lint               # Lint with Ruff
task typecheck          # Type check with MyPy
task security           # Security scans (Bandit & Safety)
task pre-commit-install # Install pre-commit hooks
```

---

## 📝 Database Operations

| Command | Description |
| --- | --- |
| `task db-upgrade` | 📈 Apply all migrations |
| `task db-migration MESSAGE="desc"` | ✨ Create new migration |
| `task db-downgrade` | 📉 Rollback last migration |
| `task db-reset` | ⚠️ Reset database (destructive) |
| `task db-history` | 📜 Show migration history |
| `task db-current` | 📍 Show current version |

---

## 🌐 API Documentation

Once the application is running, explore the interactive API documentation:

| Documentation | URL | Description |
| --- | --- | --- |
| 📘 **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API testing |
| 📗 **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Clean API reference |
| 🔍 **OpenAPI JSON** | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) | Raw OpenAPI spec |

---

## 🐳 Docker Commands

```bash
task docker-build       # 🏗️ Build Docker images
task docker-up          # ▶️ Start all containers
task docker-down        # ⏹️ Stop all containers
task docker-logs        # 📋 View container logs
task docker-clean       # 🧹 Clean unused resources
task docker-restart     # 🔄 Restart containers
```

---

## 🛡️ Security & Quality Checklist

- [x] 🔒 Security scanning with Bandit
- [x] 📦 Dependency vulnerability checks
- [x] 🎨 Consistent code formatting
- [x] 🔍 Static type checking
- [x] ✅ Comprehensive test coverage
- [x] 🪝 Pre-commit hooks for quality gates
- [x] 📝 Structured logging
- [x] ⚙️ Environment-based configuration

---

## 🤝 Contributing

We love contributions! Here's how to get started:

1. 🍴 **Fork** the repository
2. 🌿 **Create** a feature branch

   ```bash
   git checkout -b feature/amazing-feature
   ```

3. ✨ **Make** your changes
4. 🧪 **Test** your changes

   ```bash
   task test
   ```

5. 🎨 **Format** and lint

   ```bash
   task format && task lint
   ```

6. 💾 **Commit** your changes

   ```bash
   git commit -m "Add amazing feature"
   ```

7. 📤 **Push** to your fork

   ```bash
   git push origin feature/amazing-feature
   ```

8. 🎯 **Open** a Pull Request

### Code Style Guidelines

- Follow **PEP 8** conventions
- Write **meaningful commit messages**
- Add **tests** for new features
- Update **documentation** as needed
- Ensure all **checks pass** before submitting

---

## 📦 Deployment

### Production Checklist

- [ ] ✅ Set proper environment variables
- [ ] 🔒 Use HTTPS with SSL certificates
- [ ] 🌐 Configure reverse proxy
- [ ] 🔗 Set up database connection pooling
- [ ] 📊 Implement monitoring and logging
- [ ] ⚡ Enable Redis for caching
- [ ] 🛡️ Configure rate limiting
- [ ] 💓 Set up health checks
- [ ] 📈 Configure auto-scaling
- [ ] 🔐 Implement security headers

### Recommended Stack

```text
User → WorkMate API → PostgreSQL
                  ↘ Redis Cache
```

---

## 💡 Pro Tips

### 🔍 Quick Debugging

```bash
# Check running containers
docker ps

# Follow logs in real-time
task docker-logs

# Access database
task db-shell

# API health check
curl http://localhost:8000/health
```

### ⚡ Performance Optimization

- Enable Redis caching for frequently accessed data
- Use database connection pooling
- Implement query optimization with indexes
- Enable response compression
- Use async operations where possible

### 🧪 Testing Best Practices

- Write tests before implementing features (TDD)
- Aim for >80% code coverage
- Use fixtures for test data
- Mock external dependencies
- Test edge cases and error handling

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with ❤️ using:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit
- [PostgreSQL](https://www.postgresql.org/) - Reliable database
- [Redis](https://redis.io/) - In-memory data store
- [Docker](https://www.docker.com/) - Containerization platform

---

**[⬆ Back to Top](#-workmate)**

Made with ❤️ by the WorkMate Team
