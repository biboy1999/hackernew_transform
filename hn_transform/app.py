from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import hn_transform.api

if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=True)
    pass
