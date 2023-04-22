from flask import Flask, request, jsonify 
import queue 
import threading


app = Flask(__name__)
queue = queue.Queue()

@app.route('/post_data/', methods=['POST'])
def get_data():
    data = request.get_json()
    domain = data.get('domain')
    mail = data.get('email')

    print(domain, mail)
    return [domain, mail]

@app.route('/')
def index():
    return "hello world"

if __name__ == "__main__":
    app.run()