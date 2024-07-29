from flask import Flask, jsonify, Blueprint
import csv
import random
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for API v1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def load_duas():
    duas_by_chapter = {}
    current_chapter = ""
    try:
        with open('duas.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                chapter = row['Chapter']
                if chapter == "Uncategorized":
                    chapter = current_chapter
                    row['Chapter'] = current_chapter  # Update the row data
                else:
                    current_chapter = chapter
                
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

duas = load_duas()

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded", "description": str(e.description)}), 429

@api_v1.route('/duas', methods=['GET'])
@limiter.limit("100 per day")
def get_duas():
    if not duas:
        return jsonify({"error": "No duas available"}), 404
    return jsonify(duas)

@api_v1.route('/duas/<int:chapter_id>', methods=['GET'])
@limiter.limit("200 per day")
def get_dua(chapter_id):
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

@api_v1.route('/duas/<int:chapter_id>/<int:dua_id>', methods=['GET'])
@limiter.limit("300 per day")
def get_individual_dua(chapter_id, dua_id):
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

@api_v1.route('/duadaily', methods=['GET'])
@limiter.limit("50 per day")
def get_dua_of_the_day():
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

# Register the Blueprint
app.register_blueprint(api_v1)

if __name__ == '__main__':
    app.run(debug=True)
