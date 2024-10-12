# app.py

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)


def get_stock_symbols_from_csv(csv_file):
    stock_symbols = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the stock symbols are in the first column of the CSV file
            stock_symbols.append(row[0])
    return stock_symbols

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("auto_complete_index.html")

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('query', '')

    # Load stock symbols from CSV file
    csv_file = 'list_of_symbols.csv'
    stock_symbols = get_stock_symbols_from_csv(csv_file)

    # Filter stock symbols based on query
    suggestions = [symbol for symbol in stock_symbols if query.lower() in symbol.lower()]

    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    app.run(debug=True)
