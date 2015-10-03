from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def main_page():
    return render_template('index.html')

def search_graph():
	return "Hi!"

if __name__ == "__main__":
    app.run(debug=True)