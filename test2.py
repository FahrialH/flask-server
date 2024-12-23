import numpy as np
import neurokit2 as nk
import pywt
from PIL import Image
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
import bcrypt
from machine_learning import make_heart_attack_prediction

# Flask App Initialization
app = Flask(__name__)

# mysql database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/ecgdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(128), nullable=False)

class HeartAttack(db.Model):
    __tablename__ = 'heart_attack'
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), primary_key=True)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    chest = db.Column(db.String(50), nullable=False)
    smoking = db.Column(db.Boolean, nullable=False)
    abnormality = db.Column(db.String(50), nullable=False)

class ECG(db.Model):
    __tablename__ = 'ecg'
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), primary_key=True)
    ecg_scan_key = db.Column(db.String(50), primary_key=True)
    raw_ecg_data = db.Column(db.LargeBinary)


# Parameters
sample_rate = 512
before_rpeak = int(0.32 * sample_rate)
after_rpeak = int(0.48 * sample_rate)
output_size = (128, 128)
n_scales = 128
scales = np.arange(1, n_scales + 1)
waveletname = 'gaus1'
n_choices = 9
rpeak_offset = 2

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not password:
            return jsonify({"error": "This credentials combination does not exists", "status": "failed"}), 400

        if not email:
            if not phone_number:
                return jsonify({"error": "Missing fields", "status": "failed"}), 400
            user = User.query.filter((User.phone_number == phone_number)).first()
        else:
            user = User.query.filter((User.email == email)).first()

        if not user:
            return jsonify({"error": "This credentials combination does not exist", "status": "failed"}), 400

        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({"error": "Invalid password", "status": "failed"}), 400

        return jsonify({"userid": user.userid, "status": "success"}), 201

    except Exception as e:
        print("Error during login:", str(e))
        return jsonify({"error": str(e), "status": "failed"}), 500
    
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not email or not phone_number or not password:
            return jsonify({"error": "Missing required fields"}), 400

        existing_user = User.query.filter((User.email == email)).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(email=email, phone_number=phone_number, password=hashed_password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"userid": new_user.userid}), 201

    except Exception as e:
        print("Error during user registration:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/cwt', methods=['GET', 'POST'])
def get_cwt_list():
    """
    Process ECG data uploaded as binary and return CWT-transformed segments.
    """
    try:
        # parse json data
        data = request.get_json()

        # Validate User ID
        userid = request.headers.get('userid')
        if not userid or not User.query.get(userid):
            return jsonify({"error": "invalid or missing userid"}), 400
        
        userid = data['userid']
        
        # Read binary data from the request
        raw_data = request.data  # Flask stores raw binary data in request.data
        dtype = np.dtype(np.float32).newbyteorder('>')
        data = np.frombuffer(raw_data, dtype=dtype)

        # Log the received data for debugging
        print("Raw data received:", data)
        print("Length of raw data:", len(data))

        if len(data) < 18:
            return jsonify({"error": "input data length must be greater than 18"}), 400
        
        
        # Process ECG data
        data = nk.ecg_clean(data, sampling_rate=sample_rate)
        processed_data, _ = nk.ecg_process(data, sampling_rate=sample_rate)
        rpeaks = np.nonzero(np.array(processed_data['ECG_R_Peaks']))[0]
        n_rpeaks = len(rpeaks)

        # Initialize results
        item_list = []

        # Extract segments and compute CWT
        for i in range(min(n_rpeaks - 2, n_choices)):
            segment = data[
                rpeaks[i + rpeak_offset] - before_rpeak:rpeaks[i + rpeak_offset] + after_rpeak + 1
            ]
            segment, _ = pywt.cwt(segment, scales, waveletname)
            segment = Image.fromarray(segment.astype(np.float32))
            resized_segment = segment.resize(output_size)
            item_list.append({"values": list(resized_segment.getdata())})

        # Store raw ecg data
        ecg_scan_key = f"scan_{datetime.timezone.utc().strftime('%Y%m%d%H%M%S')}"
        new_ecg = ECG(userid=userid, ecg_scan_key=ecg_scan_key, raw_ecg_data=data.tobytes)
        db.session.add(new_ecg)
        db.session.commit()

        # Return the results as JSON
        # Retrieve the ecg result in json format by performing GET request on "raw_data" 
        return jsonify({
            "user_id": userid,
            "ecg_scan_key": ecg_scan_key,
            "raw_data": data.tolist(),  # Convert NumPy array to list for JSON serialization
            "items": item_list
        }), 200

    except Exception as e:
        print("Error during processing:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/test_db', methods=['GET'])
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"message": "Database connection successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/heart-attack-prediction', methods=['POST'])
def get_prediction():
    anomaly = request.json['anomaly']
    sex = request.json['sex']
    age = request.json['age']
    chest_pain = request.json['chest_pain']
    smoking = request.json['smoking']

    print(anomaly, sex, age, chest_pain, smoking,)

    prediction = make_heart_attack_prediction(sex, age, chest_pain, smoking, anomaly)
    prediction = {'prediction': prediction}
    return jsonify(prediction)

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
        existing_admin = User.query.filter_by(email='admin@gmail.com').first()
        if not existing_admin:
            admin_password = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt())
            admin_user = User(email="admin@gmail.com", phone_number="0980000000", password=admin_password.decode('utf-8'))
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: admin@gmail.com")
    
    app.run(host='0.0.0.0', port=8000)
