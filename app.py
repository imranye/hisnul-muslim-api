# Import necessary modules
from flask import Flask, jsonify, Blueprint
import csv
import random
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Initialize Flask application
app = Flask(__name__)
# Configure logging to INFO level
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for API v1
# This allows for better organization and versioning of the API
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Initialize rate limiter
# This helps prevent abuse of the API by limiting request frequency
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Store rate limiting data in memory
)

# Initialize Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def load_duas():
    """
    Load duas from a CSV file and organize them by chapter.
    
    Returns:
    dict: A dictionary where keys are chapter names and values are lists of duas.
    """
    duas_by_chapter = {}
    current_chapter = ""
    try:
        with open('duas.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                chapter = row['Chapter']
                # Handle 'Uncategorized' duas by assigning them to the current chapter
                if chapter == "Uncategorized":
                    chapter = current_chapter
                    row['Chapter'] = current_chapter  # Update the row data
                else:
                    current_chapter = chapter
                
                # Create a new list for the chapter if it doesn't exist
                if chapter not in duas_by_chapter:
                    duas_by_chapter[chapter] = []
                duas_by_chapter[chapter].append(row)
        return duas_by_chapter
    except FileNotFoundError:
        logging.error("duas.csv file not found")
        return {}
    except csv.Error as e:
        logging.error(f"Error reading CSV file: {e}")
        return {}

# Load duas at startup
duas = load_duas()

# Error handlers for common HTTP status codes
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded", "description": str(e.description)}), 429

# API route to get all duas
@api_v1.route('/duas', methods=['GET'])
@limiter.limit("100 per day")
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_duas():
    """
    Retrieve all duas.
    
    Returns:
    JSON: All duas organized by chapter, or an error if no duas are available.
    """
    if not duas:
        return jsonify({"error": "No duas available"}), 404
    return jsonify(duas)

# API route to get duas for a specific chapter
@api_v1.route('/duas/<int:chapter_id>', methods=['GET'])
@limiter.limit("200 per day")
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_dua(chapter_id):
    """
    Retrieve duas for a specific chapter.
    
    Args:
    chapter_id (int): The ID of the chapter.
    
    Returns:
    JSON: Duas for the specified chapter, or an error if the chapter is not found.
    """
    try:
        chapters = list(duas.keys())
        if 0 <= chapter_id < len(chapters):
            chapter = chapters[chapter_id]
            return jsonify(duas[chapter])
        else:
            return jsonify({"error": "Chapter not found"}), 404
    except Exception as e:
        logging.error(f"Error in get_dua: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API route to get a specific dua from a specific chapter
@api_v1.route('/duas/<int:chapter_id>/<int:dua_id>', methods=['GET'])
@limiter.limit("300 per day")
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_individual_dua(chapter_id, dua_id):
    """
    Retrieve a specific dua from a specific chapter.
    
    Args:
    chapter_id (int): The ID of the chapter.
    dua_id (int): The ID of the dua within the chapter.
    
    Returns:
    JSON: The specified dua, or an error if the chapter or dua is not found.
    """
    try:
        chapters = list(duas.keys())
        if 0 <= chapter_id < len(chapters):
            chapter = chapters[chapter_id]
            chapter_duas = duas[chapter]
            if 0 <= dua_id < len(chapter_duas):
                return jsonify(chapter_duas[dua_id])
            else:
                return jsonify({"error": "Dua not found in this chapter"}), 404
        else:
            return jsonify({"error": "Chapter not found"}), 404
    except Exception as e:
        logging.error(f"Error in get_individual_dua: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API route to get a random dua (Dua of the Day)
@api_v1.route('/duadaily', methods=['GET'])
@limiter.limit("50 per day")
@cache.cached(timeout=86400)  # Cache for 24 hours
def get_dua_of_the_day():
    """
    Retrieve a random dua as the Dua of the Day.
    
    Returns:
    JSON: A randomly selected dua, or an error if no duas are available.
    """
    try:
        all_duas = []
        for chapter_duas in duas.values():
            all_duas.extend(chapter_duas)
        if all_duas:
            return jsonify(random.choice(all_duas))
        else:
            return jsonify({"error": "No duas available"}), 404
    except Exception as e:
        logging.error(f"Error in get_dua_of_the_day: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Register the Blueprint with the Flask application
app.register_blueprint(api_v1)

# Run the application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)  # Note: Set debug=False in production
