from flask import Flask, request
from two import apiCall
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def train():
    d = json.loads((request.data).decode('utf-8'))
    return apiCall(d)

@app.route('/test', methods=['GET', 'POST'])
def testApi():
    return "success"

app.run(port=5000)