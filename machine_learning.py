import joblib
import pandas as pd
import os

def make_heart_attack_prediction(sex, age, chest_pain, smoking, abnormality):
    prediction = True
    # insert ml model here
    test_data = pd.DataFrame({
        'sex': sex,
        'age': age,
        'chest_pain': chest_pain,
        'smoking': smoking,
        'abnormality': abnormality,
    })
    basedir = os.path.abspath(os.path.dirname(__file__))
    model, refs_cols, target_column = joblib.load(f"{basedir}/HA-model.pkl")
    X_test = test_data
    predictions = model.pre
    return prediction


basedir = os.path.abspath(os.path.dirname(__file__))
model, refs_cols, target_column = joblib.load(f"{basedir}/HA-model.pkl")
print(basedir)
print(refs_cols)
print(target_column)