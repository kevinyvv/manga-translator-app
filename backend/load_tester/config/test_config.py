# This file contains configuration settings for the load tests.

BASE_URL = "http://localhost:5000"  # Base URL for the Manga Translator app
NUM_USERS = 100  # Number of simulated users
HATCH_RATE = 10  # Rate at which users are spawned
TEST_DURATION = 60  # Duration of the test in seconds

# Define any other constants or settings as needed for the load tests.