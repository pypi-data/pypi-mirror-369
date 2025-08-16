# xarchgen

Generate Clean Architecture backend applications (FastAPI/DotNet) from PostgreSQL database schemas.

## Installation

```bash
# Install from PyPI (once published)
pip install xarchgen

# Or with uv
uv add xarchgen

# Or install from source
git clone <repository-url>
cd xarchgen-package
uv pip install -e .
```

## Quick Start

### Generate a FastAPI application

```bash
xarchgen create fastapi --database "postgresql://user:pass@localhost:5432/mydb"
```

### Generate a .NET Core application

```bash
xarchgen create dotnet --database "postgresql://user:pass@localhost:5432/mydb" --name MyApp
```

## Commands

### `xarchgen create`

Generate a new backend application from your PostgreSQL database schema.

**Arguments:**
- `framework`: Choose between `fastapi` or `dotnet`

**Options:**
- `--database`, `-d`: PostgreSQL connection string (required)
- `--output`, `-o`: Output directory (default: `./generated-app`)
- `--name`, `-n`: Application/Solution name (default: `GeneratedApp`)
- `--group-by`, `-g`: Table grouping strategy:
  - `schema`: Group by database schema (default)
  - `prefix`: Group by table name prefix (e.g., `user_accounts`, `user_profiles` → `User` group)
  - `none`: Put all tables in a single "General" group
- `--zip`, `-z`: Generate a ZIP file instead of a directory
- `--tables`, `-t`: Include only specific tables (can be used multiple times)
- `--exclude`, `-e`: Exclude specific tables (can be used multiple times)
- `--verbose`, `-v`: Show detailed progress

**Examples:**

```bash
# Basic FastAPI generation
xarchgen create fastapi -d "postgresql://user:pass@localhost/db"

# .NET with custom name and output
xarchgen create dotnet -d "postgresql://..." -n MyProject -o ./my-project

# Group tables by prefix and create ZIP
xarchgen create fastapi -d "postgresql://..." --group-by prefix --zip

# Include only specific tables
xarchgen create fastapi -d "postgresql://..." -t users -t orders -t products

# Exclude certain tables
xarchgen create dotnet -d "postgresql://..." -e logs -e temp_data
```

### `xarchgen inspect`

Inspect your database schema without generating code.

```bash
xarchgen inspect --database "postgresql://user:pass@localhost:5432/mydb"
```

## Generated Architecture

### FastAPI Applications

```
src/
├── api/
│   ├── main.py              # FastAPI app entry point
│   ├── dependencies.py      # Dependency injection
│   ├── middleware/          # Custom middleware
│   └── v1/routers/         # API route handlers
├── application/
│   ├── dto/                # Data transfer objects
│   └── services/           # Business logic services
├── core/
│   ├── entities/           # Domain models
│   ├── interfaces/         # Repository contracts
│   └── exceptions/         # Custom exceptions
├── infrastructure/
│   ├── database/
│   │   ├── models/         # SQLAlchemy models
│   │   └── repositories/   # Repository implementations
│   └── config/            # Database configuration
├── common/
│   ├── logging.py         # Logging configuration
│   ├── pagination.py      # Pagination utilities
│   └── result.py          # Result pattern
└── config/
    ├── settings.py        # Application settings
    └── main.py           # Configuration entry point
```

### .NET Core Applications

```
src/
├── Core/
│   ├── Entities/          # Domain models
│   ├── Interfaces/        # Repository contracts
│   └── Common/           # Result pattern, errors
├── Application/
│   ├── Services/         # Business logic services
│   ├── Interfaces/       # Service contracts
│   ├── DTOs/            # Data transfer objects
│   ├── Validators/      # FluentValidation validators
│   └── Mappings/        # AutoMapper profiles
├── Infrastructure/
│   ├── Data/            # Repository implementations (Dapper)
│   └── Configuration/   # Database configuration
└── WebApi/
    ├── Controllers/     # API controllers
    ├── Middleware/      # Custom middleware
    └── Configuration/   # App configuration
```

## Features

- **Clean Architecture**: Follows Clean Architecture principles with proper layer separation
- **Database-First**: Generates code from existing PostgreSQL database schemas
- **Table Grouping**: Organize tables into logical groups (by schema, prefix, or manual)
- **Type Safety**: Proper type mappings from PostgreSQL to target language
- **Modern Patterns**: 
  - Result pattern for error handling
  - Repository pattern for data access
  - Dependency injection
  - Structured logging
  - API versioning
- **Production Ready**: 
  - Error handling middleware
  - Request correlation IDs
  - Swagger/OpenAPI documentation
  - Health checks
  - Docker support
- **Extensible**: Easy to modify generated templates

## Connection String Formats

PostgreSQL URL format (recommended):
```
postgresql://username:password@host:port/database
```

Alternative formats:
```
postgres://username:password@host:port/database
Host=localhost;Port=5432;Database=mydb;Username=user;Password=pass
```

## Generated Application Setup

### FastAPI

```bash
cd generated-app
cp .env.example .env  # Configure your database connection
uv sync               # Install dependencies
uv run alembic upgrade head  # Run migrations
uv run uvicorn src.api.main:app --reload  # Start server
```

Access API documentation at: `http://localhost:8000/docs`

### .NET Core

```bash
cd generated-app
# Update appsettings.json with your connection string
dotnet restore        # Restore dependencies
dotnet build         # Build solution
dotnet run --project src/WebApi  # Start server
```

Access API documentation at: `https://localhost:5001/swagger`

## Development

```bash
git clone <repository-url>
cd xarchgen-package
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black xarchgen/
ruff check xarchgen/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/Xcdify/DotNetCoreBackendGenerator/issues)
- Documentation: [Full documentation](https://github.com/Xcdify/DotNetCoreBackendGenerator#readme)