# Finance API

A RESTful API for personal finance management, built with FastAPI and SQLAlchemy. This API allows you to track accounts, transactions, budget categories, and savings goals.

## Features

- Account management (create, read, update, delete)
- Transaction tracking with filtering
- Budget category management
- Savings bucket/goal tracking
- Built with FastAPI and SQLAlchemy
- Comprehensive test coverage
- Containerized with Docker

## Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Docker (optional, for containerization)
- pip (Python package manager)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd finance-api
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/finance_db

# For testing
TESTING=false
```

For local development, you can also create a `.env.local` file which will override the `.env` file.

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt  # For development and testing
```

## Database Setup

### Local Development (SQLite)

For development, you can use SQLite by setting the following in your `.env.local`:

```env
DATABASE_URL=sqlite:///./finance.db
```

### Production (PostgreSQL)

1. Install PostgreSQL if you haven't already
2. Create a new database:
   ```bash
   createdb finance_db
   ```
3. Update the `DATABASE_URL` in your `.env` file with your PostgreSQL credentials

## Running the Application

### Development Mode

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t finance-api .
   ```

2. Run the container:
   ```bash
   docker run -d --name finance-api -p 8000:8000 --env-file .env finance-api
   ```

## API Documentation

Once the application is running, you can access the following:

- **Interactive API Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **Alternative API Docs (ReDoc)**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

## Running Tests

### Run All Tests

```bash
pytest -v
```

### Run Tests with Coverage Report

```bash
pytest --cov=src --cov-report=html
```

The coverage report will be available in the `htmlcov` directory.

### Run a Specific Test File

```bash
pytest tests/test_models.py -v
```

### Run a Specific Test Function

```bash
pytest tests/test_models.py::test_create_account -v
```

## Project Structure

```
finance-api/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic models
│   ├── crud.py             # Database operations
│   ├── database.py         # Database configuration
│   └── routers/            # API route handlers
│       ├── __init__.py
│       ├── accounts.py
│       ├── budgets.py
│       ├── savings_buckets.py
│       └── transactions.py
├── tests/                  # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_crud.py
│   ├── test_database.py
│   └── test_models.py
├── .env.example           # Example environment variables
├── .gitignore
├── Dockerfile
├── requirements.txt       # Production dependencies
├── requirements-test.txt  # Development dependencies
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
