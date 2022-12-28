from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'JAsuran2p0'


if __name__ == "__main__":
    app.run()
