from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/menu')
def menu():
    return render_template("menu.html")

@app.route('/about-us')
def about_us():
    return render_template("about-us.html")

if __name__ == '__main__':
    app.run(debug=True, port=8080)

