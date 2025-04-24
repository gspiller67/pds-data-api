# PDS Data API

A FastAPI-based REST API application for managing PDS data.

## Features

- RESTful API endpoints for CRUD operations
- FastAPI with automatic OpenAPI documentation
- Pydantic models for request/response validation
- Async support
- Development server with auto-reload

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd pds-data-api
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To start the development server:

```bash
python main.py
```

Or alternatively:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

- `GET /`: Root endpoint, returns API information
- `GET /items`: Get all items
- `GET /items/{item_id}`: Get a specific item by ID
- `POST /items`: Create a new item
- `PUT /items/{item_id}`: Update an existing item
- `DELETE /items/{item_id}`: Delete an item

## Example Usage

### Creating a new item

```bash
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{"id": 1, "name": "Test Item", "description": "This is a test item", "price": 29.99}'
```

### Getting all items

```bash
curl "http://localhost:8000/items"
```

## Development

This is a basic setup that uses an in-memory list to store data. For production use, consider:

1. Adding a proper database (e.g., PostgreSQL, MongoDB)
2. Implementing authentication and authorization
3. Adding input validation and sanitization
4. Implementing proper error handling
5. Adding logging
6. Setting up environment variables
7. Adding tests

## License

[MIT License](LICENSE) 