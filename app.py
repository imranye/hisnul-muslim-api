from flask import Flask, jsonify
import csv
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

@app.route('/api/duas', methods=['GET'])
def get_duas():
    if not duas:
        return jsonify({"error": "No duas available"}), 404
    return jsonify(duas)

@app.route('/api/duas/<int:chapter_id>', methods=['GET'])
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

@app.route('/api/duas/<int:chapter_id>/<int:dua_id>', methods=['GET'])
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

@app.route('/api/duadaily', methods=['GET'])
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

if __name__ == '__main__':
    app.run(debug=True)
