import numpy as np
import neurokit2 as nk
import pywt
from PIL import Image
from flask import Flask, request, jsonify

# Flask App Initialization
app = Flask(__name__)

# Parameters for CWT
sample_rate = 512
before_rpeak = int(0.32 * sample_rate)
after_rpeak = int(0.48 * sample_rate)
output_size = (128, 128)
n_scales = 128
scales = np.arange(1, n_scales + 1)
waveletname = 'gaus1'
n_choices = 9
rpeak_offset = 2

signal_data = []

@app.route('/cwt', methods=['GET', 'POST'])
def get_cwt_list():
    """
    Process ECG data uploaded as binary and return CWT-transformed segments.
    """
    try:
        # # Read binary data from the request
        # raw_data = request.data  # Flask stores raw binary data in request.data
        # dtype = np.dtype(np.float32).newbyteorder('>')
        # data = np.frombuffer(raw_data, dtype=dtype)

        # # Log the received data for debugging
        # print("Raw data received:", data)
        # print("Length of raw data:", len(data))

        global signal_data

        # if len(data) < 18:
        #     return jsonify({"error": "input data length must be greater than 18"}), 400
        
        # Process ECG data
        print(f"Signal data size: {len(signal_data)}")
        data = nk.ecg_clean(signal_data, sampling_rate=sample_rate)
        print(f"Cleaned data size: {len(data)}")
        # processed_data, _ = nk.ecg_process(data, sampling_rate=sample_rate)
        # rpeaks = np.nonzero(np.array(processed_data['ECG_R_Peaks']))[0]
        # n_rpeaks = len(rpeaks)

        # # Initialize results
        # item_list = []

        # # Extract segments and compute CWT
        # for i in range(min(n_rpeaks - 2, n_choices)):
        #     segment = data[
        #         rpeaks[i + rpeak_offset] - before_rpeak:rpeaks[i + rpeak_offset] + after_rpeak + 1
        #     ]
        #     segment, _ = pywt.cwt(segment, scales, waveletname)
        #     segment = Image.fromarray(segment.astype(np.float32))
        #     resized_segment = segment.resize(output_size)
        #     item_list.append({"values": list(resized_segment.getdata())})
        
        # Reset the signal data array
        signal_data = []
        # Return the results as JSON
        # return jsonify({
        #     "raw_data": data.tolist(),  # Convert NumPy array to list for JSON serialization
        #     "items": item_list
        # }), 200
        return jsonify({
            "raw_data": data.tolist(),  # Convert NumPy array to list for JSON serialization
        }), 200

    except Exception as e:
        print("Error during processing:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/upload-signal', methods=['POST'])
def upload_signal():
    global signal_data
    raw_data = request.data
    dtype = np.dtype(np.float32).newbyteorder('>')
    data = np.frombuffer(raw_data, dtype=dtype)
    signal_data.extend(data)
    print(f"Chunk received, size: {len(data)}")
    print(f"Signal data total size: {len(signal_data)}")
    return {
        "status": "received",
        "chunk_size": len(data) 
    }


@app.route('/heart-attack-prediction', methods=['POST'])
def get_prediction():
    sex = request.json['sex']
    age = request.json['age']
    chest_pain = request.json['chest_pain']
    smoking = request.json['smoking']
    abnormality = request.json['abnormality']

    print(sex, age, chest_pain, smoking, abnormality,)

    prediction = make_heart_attack_prediction(sex, age, chest_pain, smoking, abnormality)
    prediction = {'prediction': prediction}
    return jsonify(prediction)



def make_heart_attack_prediction(sex, age, chest_pain, smoking, abnormality):
    prediction = True
    # insert ml model here
    return prediction

if __name__ == '__main__':
    
    #with app.app_context():
        #db.create_all()
    
    # Run the Flask server on port 8000
    app.run(host='0.0.0.0', port=8000, debug=True)
