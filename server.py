from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def api():
    return "Hello, World!"

@app.route('/testPost', methods=['POST'])
def testPost():
    data = request.get_json()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)