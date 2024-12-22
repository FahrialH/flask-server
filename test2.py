import numpy as np
import neurokit2 as nk
import pywt
from PIL import Image
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Flask App Initialization
app = Flask(__name__)

# # mysql database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ecgdb'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # Models
# class User(db.Model):
#     __tablename__ = 'user'
#     userid = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     phone_number = db.Column(db.String(15), nullable=False)
#     password = db.Column(db.String(128), nullable=False)

# # class HeartAttack(db.Model):
#     __tablename__ = 'heart_attack'
#     userid = db.Column(db.Integer, db.ForeignKey('user.userid'), autoincrement=True, primary_key=True)
#     sex = db.Column(db.String(10), nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     chest = db.Column(db.String(50), nullable=False)
#     smoking = db.Column(db.Boolean, nullable=False)
#     abnormality = db.Column(db.String(50), nullable=False)

# # class ECG(db.Model):
#     __tablename__ = 'ecg'
#     userid = db.Column(db.Integer, db.ForeignKey('user.userid'), primary_key=True)
#     ecg_scan_key = db.Column(db.String(50), primary_key=True)

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

@app.route('/cwt', methods=['GET', 'POST'])
def get_cwt_list():
    """
    Process ECG data uploaded as binary and return CWT-transformed segments.
    """
    try:
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

        # Return the results as JSON
        return jsonify({
            "raw_data": data.tolist(),  # Convert NumPy array to list for JSON serialization
            "items": item_list
        }), 200

    except Exception as e:
        print("Error during processing:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    
    #with app.app_context():
        #db.create_all()
    
    # Run the Flask server on port 8000
    app.run(host='0.0.0.0', port=8000, debug=True)
