import joblib
import pandas as pd
import os

def make_heart_attack_prediction(sex, age, chest_pain, smoking, anomaly):
    # insert ml model here
    test_data = pd.DataFrame({
        'sex': sex,
        'age': age,
        'cp': chest_pain,
        'restecg': anomaly,
        'exang': smoking,
    }, index=[0])
    basedir = os.path.abspath(os.path.dirname(__file__))
    model, refs_cols, target_column = joblib.load(f"{basedir}/HA-model.pkl")
    X_test = test_data
    predictions = model.predict(X_test)
    return predictions.squeeze() != 0
    # return prediction

# to try
make_heart_attack_prediction(1, 80, 1, 0, 0)