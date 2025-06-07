# Backend Setup (Flask + Poetry)

This backend provides a simple Flask API for your project. It uses [Poetry](https://python-poetry.org/) for dependency management.

## Prerequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/docs/#installation)

## Setup Instructions

1. **Clone the repository** (if you haven’t already):

   ```sh
   git clone <your-repo-url>
   cd manga-translator/backend
   ```

2. **Install dependencies with Poetry:**

   ```sh
   poetry install
   ```

3. **Activate the Poetry virtual environment:**

   ```sh
   poetry shell
   ```

4. **Run the Flask app:**

   ```sh
   poetry run python app.py
   ```

   The API will be available at [http://127.0.0.1:5000/api/hello](http://127.0.0.1:5000/api/hello).

## API Example

- **GET** `/api/hello`  
  Returns:  
  ```json
  { "message": "Hello from Flask!" }
  ```

## Development Notes

- Dependencies are managed in `pyproject.toml`.
- To add a new dependency, use:  
  ```sh
  poetry add <package-name>
  ```
- To exit the Poetry shell, type `exit`.

---