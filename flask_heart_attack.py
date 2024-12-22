from flask import Flask, request, jsonify
import os
app = Flask(__name__)

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
    app.run(port=8000, debug=True)