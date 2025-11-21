from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    image_names = ["trees", "sky", "city", "low saturation", "high saturation"]
    return render_template('index.html', image_names=image_names)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")