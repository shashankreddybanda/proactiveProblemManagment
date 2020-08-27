from flask import Flask, request
from two import apiCall
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def train():
    d = json.loads((request.data).decode('utf-8'))
    return apiCall(d)

@app.route('/test', methods=['GET', 'POST'])
def testApi():
    return type(request.data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)