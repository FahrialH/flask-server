import numpy as np
import neurokit2 as nk
from PIL import Image
from flask import Flask, request, jsonify

# Flask App Initialization
app = Flask(__name__)

@app.route('/heart-attack-prediction', methods=['POST'])
def get_prediction():
    sex = request.json['sex']
    age = request.json['age']
    chest_pain = request.json['chest_pain']
    smoking = request.json['smoking']
    anomaly = request.json['anomaly']

    print(sex, age, chest_pain, smoking, anomaly,)

    prediction = make_heart_attack_prediction(sex, age, chest_pain, smoking, anomaly)
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
