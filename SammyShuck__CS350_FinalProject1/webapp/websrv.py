
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello world'


@app.route('/final/')
def final():
    return render_template('static/final/StaticCanvas.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
