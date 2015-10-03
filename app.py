from flask import Flask
from flask import render_template
from flask import request
import json
from flask import jsonify


app = Flask(__name__)

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_graph():
	print "GOT HERE"
	query = request.form['query']
	return jsonify({"results":query})

if __name__ == "__main__":
    app.run(debug=True)