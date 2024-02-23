from flask import Flask, request, jsonify
from flask_sqlalchemy  import SQLAlchemy
from flask_cors import CORS, cross_origin
from datetime import datetime
from models import db, Booking, AvailableBookings, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #to supress warning
CORS(app, resources={r"/api/*": {"origins": "*"}})
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/isAlive', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def is_alive():
    return jsonify({'message': 'Alive!'}), 200

@app.route('/register', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def register():
    data = request.get_json()
    email = data['email']
    username = data['username']
    password = data['password']
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
