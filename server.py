# LiteChat 0.0.1

from flask import Flask, request, send_from_directory

app = Flask(__name__)


@app.route('/')
@app.route('/registration')
def index():
    with open("front/registration.html") as f:
        return f.read()

@app.route('/registration/check_all')
def check_registration():
    inp = {}
    for i in ("email", "username", "name", "password"):
        inp[i] = request.args.get(i)
    print()
    print(inp)
    return "false"

@app.route('/data/<path:filename>')
def get_image(filename):
    if True:
        print(request.remote_addr + " запросил " + filename)
        return send_from_directory('data', filename)
    else:
        print(request.remote_addr + " запросил " + filename + " - ОТКАЗАНО!")

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

