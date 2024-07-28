from flask import Flask, jsonify
import csv

app = Flask(__name__)

# Load the data from the CSV file
def load_duas():
    duas = []
    with open('duas.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            duas.append(row)
    return duas

duas = load_duas()

@app.route('/api/duas', methods=['GET'])
def get_duas():
    return jsonify(duas)

@app.route('/api/duas/<int:dua_id>', methods=['GET'])
def get_dua(dua_id):
    if 0 <= dua_id < len(duas):
        return jsonify(duas[dua_id])
    else:
        return jsonify({"error": "Dua not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
