import pickle
import pandas as pd
import os
import tensorflow_decision_forests as tfdf

def make_heart_attack_prediction(sex, age, chest_pain, smoking, anomaly):
    test_data = pd.DataFrame({
        'sex': [sex],
        'age': [age],
        'cp': [chest_pain],
        'restecg': [anomaly],
        'exang': [smoking],
    })

    basedir = os.path.abspath(os.path.dirname(__file__))

    model_file_path = os.path.join(basedir, "HA-model.pkl")
    with open(model_file_path, 'rb') as file:
        model, refs_cols, target_column = pickle.load(file)
        print(f"model: {model} || refs_cols: {refs_cols} || taget_column: {target_column}")

    predictions = model.predict(test_data)
    print(f"Prediction objcet: {predictions}")
    prediction_result = 0 if predictions.squeeze() == 0.0 else 1
    print(f"Prediction: {prediction_result}")
    return prediction_result
