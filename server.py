from flask import Flask, send_file, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="3">
    <style>
        body { background: black; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        img { max-width: 100%; border: 1px solid #333; }
    </style>
</head>
<body>
    <img src="/image" />
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/image")
def image():
    return send_file("current.png", mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
