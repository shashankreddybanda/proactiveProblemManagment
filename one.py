from flask import Flask, request
from two import apiCall
from three import getRecords
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def train():
    d = json.loads((request.data).decode('utf-8'))
    return apiCall(d)

@app.route('/test', methods=['GET', 'POST'])
def testApi():
    data = getRecords()
    print(data["result"][0])
    return str(type(request.data))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 33507))
    app.run(host='0.0.0.0', port=port)