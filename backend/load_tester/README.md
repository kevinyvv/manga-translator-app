# Manga Translator Load Tests

This project contains load tests for the Manga Translator application using Locust. The tests simulate user interactions with the application to evaluate its performance under various conditions.

## Project Structure

- **locustfiles/**: Contains the load testing scripts and tasks.
  - **manga_translator_test.py**: Main load testing script defining user behavior.
  - **tasks/**: Contains specific tasks for translation and uploading.
- **config/**: Configuration settings for the load tests.
- **data/**: Sample data used for testing.
- **utils/**: Utility functions to assist with load testing.
- **requirements.txt**: Lists the dependencies required for the project.
- **locust.conf**: Configuration settings for Locust.
  
## Running the Load Tests

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Locust load testing environment:
   ```bash
   locust -f locustfiles/manga_translator_test.py --host http://localhost:5000
   ```

3. Open your web browser and navigate to `http://localhost:8089` to access the Locust web interface.

4. Configure the number of users and spawn rate, then start the test.

## Notes

- Ensure that the Manga Translator app is running before starting the load tests.
- Modify the sample data in `data/sample_manga.json` as needed for your tests.
- Review the configuration settings in `config/test_config.py` to customize the test behavior.