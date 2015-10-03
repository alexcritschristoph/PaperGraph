from flask import Flask
from flask import render_template
from flask import request
import json
from flask import jsonify
import uuid
import os

app = Flask(__name__)

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_graph():
	print "GOT HERE"
	query = request.form['query']

	#Run the esearch command
	file_name = uuid.uuid4() + ".dat"

	os.system("esearch -query '"+ query +"' -db pubmed | efetch -format Abstract -mode xml > ~/" + file_name)

	#Parse results of esearch command

	#Pass [links, nodes] to javascript
	return jsonify({"results":query})

if __name__ == "__main__":
    app.run(debug=True)