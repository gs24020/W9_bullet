from flask import Flask, send_from_directory

app = Flask(
    __name__,
    static_folder="build/web"
)


@app.route("/")
def index():

    return send_from_directory(
        "build/web",
        "index.html"
    )


@app.route("/<path:path>")
def static_proxy(path):

    return send_from_directory(
        "build/web",
        path
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )