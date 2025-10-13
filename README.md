# Manga Translator App

This application allows you to translate manga from one language to another.

## Process Example

![process](https://github.com/user-attachments/assets/e12c023b-9fc9-43ab-a006-49da8df8ca1f)

The site looks much nicer than this debug output :)

## Running the application

### Backend

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the dependencies using Poetry:
    ```bash
    poetry install
    ```
3.  Create .env and add necessary environment variables:
    ```
    GEMINI_API_KEY=<Gemini Key Here>
    ```
4.  Run the Flask application:
    ```bash
    poetry run python app.py
    ```

### Frontend

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the dependencies using npm:
    ```bash
    npm install
    ```
3.  Run the Next.js development server:
    ```bash
    npm run dev
    ```
