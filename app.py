# Import necessary modules
from flask import Flask, jsonify, Blueprint
import csv
import random
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_restx import Api, Resource, fields

# Initialize Flask application
app = Flask(__name__)
# Configure logging to INFO level
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for API v1
# This allows for better organization and versioning of the API
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Initialize Flask-RESTX
api = Api(api_v1, version='1.0', title='Hisnul Muslim API',
          description='API for retrieving duas from Hisnul Muslim')

# Initialize rate limiter
# This helps prevent abuse of the API by limiting request frequency
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"],
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

# Define models for Swagger documentation
dua_model = api.model('Dua', {
    'Chapter': fields.String(required=True, description='Chapter name'),
    'Reference': fields.String(required=True, description='Reference number'),
    'Arabic': fields.String(required=True, description='Dua in Arabic'),
    'English': fields.String(required=True, description='English translation of the dua'),
    'Transliteration': fields.String(required=True, description='Transliteration of the dua')
})

# API route to get all duas
@api.route('/duas')
class AllDuas(Resource):
    @api.doc('get_all_duas')
    @limiter.limit("100 per day")
    @cache.cached(timeout=3600)  # Cache for 1 hour
    def get(self):
        """
        Retrieve all duas
        """
        if not duas:
            api.abort(404, "No duas available")
        return jsonify(duas)

# API route to get duas for a specific chapter
@api.route('/duas/<int:chapter_id>')
class ChapterDuas(Resource):
    @api.doc('get_chapter_duas')
    @api.param('chapter_id', 'The chapter ID')
    @limiter.limit("200 per day")
    @cache.cached(timeout=3600)  # Cache for 1 hour
    def get(self, chapter_id):
        """
        Retrieve duas for a specific chapter
        """
        try:
            chapters = list(duas.keys())
            if 0 <= chapter_id < len(chapters):
                chapter = chapters[chapter_id]
                return jsonify(duas[chapter])
            else:
                api.abort(404, "Chapter not found")
        except Exception as e:
            logging.error(f"Error in get_dua: {e}")
            api.abort(500, "Internal server error")

# API route to get a specific dua from a specific chapter
@api.route('/duas/<int:chapter_id>/<int:dua_id>')
class IndividualDua(Resource):
    @api.doc('get_individual_dua')
    @api.param('chapter_id', 'The chapter ID')
    @api.param('dua_id', 'The dua ID within the chapter')
    @limiter.limit("300 per day")
    @cache.cached(timeout=3600)  # Cache for 1 hour
    def get(self, chapter_id, dua_id):
        """
        Retrieve a specific dua from a specific chapter
        """
        try:
            chapters = list(duas.keys())
            if 0 <= chapter_id < len(chapters):
                chapter = chapters[chapter_id]
                chapter_duas = duas[chapter]
                if 0 <= dua_id < len(chapter_duas):
                    return jsonify(chapter_duas[dua_id])
                else:
                    api.abort(404, "Dua not found in this chapter")
            else:
                api.abort(404, "Chapter not found")
        except Exception as e:
            logging.error(f"Error in get_individual_dua: {e}")
            api.abort(500, "Internal server error")

# API route to get a random dua (Dua of the Day)
@api.route('/duadaily')
class DuaOfTheDay(Resource):
    @api.doc('get_dua_of_the_day')
    @limiter.limit("50 per day")
    @cache.cached(timeout=86400)  # Cache for 24 hours
    def get(self):
        """
        Retrieve a random dua as the Dua of the Day
        """
        try:
            all_duas = []
            for chapter_duas in duas.values():
                all_duas.extend(chapter_duas)
            if all_duas:
                return jsonify(random.choice(all_duas))
            else:
                api.abort(404, "No duas available")
        except Exception as e:
            logging.error(f"Error in get_dua_of_the_day: {e}")
            api.abort(500, "Internal server error")

# Register the Blueprint with the Flask application
app.register_blueprint(api_v1)

# Run the application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)  # Note: Set debug=False in production
