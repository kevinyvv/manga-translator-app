def format_request_data(data):
    # Function to format request data for the load tests
    return {
        "text": data.get("text", ""),
        "language_from": data.get("language_from", "en"),
        "language_to": data.get("language_to", "ja"),
    }

def extract_manga_info(manga_data):
    # Function to extract relevant information from manga data
    return {
        "title": manga_data.get("title", ""),
        "author": manga_data.get("author", ""),
        "chapters": manga_data.get("chapters", []),
    }

def generate_random_user_id():
    # Function to generate a random user ID for testing purposes
    import random
    return f"user_{random.randint(1000, 9999)}"