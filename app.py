from flask import Flask, jsonify
import csv

app = Flask(__name__)

def load_duas():
    duas_by_chapter = {}
    with open('duas.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            chapter = row['Chapter']
            if chapter not in duas_by_chapter:
                duas_by_chapter[chapter] = []
            duas_by_chapter[chapter].append(row)
    return duas_by_chapter

duas = load_duas()

@app.route('/api/duas', methods=['GET'])
def get_duas():
    return jsonify(duas)

@app.route('/api/duas/<int:chapter_id>', methods=['GET'])
def get_dua(chapter_id):
    chapters = list(duas.keys())
    if 0 <= chapter_id < len(chapters):
        chapter = chapters[chapter_id]
        return jsonify(duas[chapter])
    else:
        return jsonify({"error": "Chapter not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
