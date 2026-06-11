import numpy as np
M1_COEF = np.array([1450.92095196])
M1_INTERCEPT = 722.1839917936694
M1_SCALER_MEAN = np.array([715.47249707])
M1_SCALER_SCALE = np.array([1438.31352529])
M2_COEF = np.array([-0.59461836, -0.8840954, 13.16175616])
M2_INTERCEPT = 1205.768485392164
M2_SCALER_MEAN = np.array([20188.04279015, 715.47249707])
M2_SCALER_SCALE = np.array([37549.96159868, 1438.31352529])
M1_R2 = 0.99
M2_R2 = 0.21

def predict_employment_level(emp_lag1: float) -> dict:
    x = np.array([[emp_lag1]])
    x_scaled = (x - M1_SCALER_MEAN) / M1_SCALER_SCALE
    prediction = (x_scaled @ M1_COEF + M1_INTERCEPT).item()
    return {'model': 'employment_level', 'input': {'employment_lag1': emp_lag1}, 'predicted_employment_thousands': round(prediction, 2)}

def predict_employment_change(graduates: float, emp_lag1: float, time: int) -> dict:
    x_to_scale = np.array([[graduates, emp_lag1]])
    x_scaled = (x_to_scale - M2_SCALER_MEAN) / M2_SCALER_SCALE
    x_full = np.array([[float(time), x_scaled[0, 0], x_scaled[0, 1]]])
    prediction = (x_full @ M2_COEF + M2_INTERCEPT).item()
    return {'model': 'employment_change', 'input': {'graduates': graduates, 'employment_lag1': emp_lag1, 'time': time}, 'predicted_change_thousands': round(prediction, 2)}

def merge_employment_models(graduates: float, emp_lag1: float, time: int, level_weight: float=None) -> dict:
    if level_weight is None:
        level_weight = M1_R2 / (M1_R2 + M2_R2)
    change_weight = 1.0 - level_weight
    level_est = predict_employment_level(emp_lag1)['predicted_employment_thousands']
    change_pred = predict_employment_change(graduates, emp_lag1, time)['predicted_change_thousands']
    change_est = emp_lag1 + change_pred
    merged_level = level_weight * level_est + change_weight * change_est
    if emp_lag1 and emp_lag1 != 0:
        outlook_growth = (merged_level - emp_lag1) / emp_lag1
    else:
        outlook_growth = 0.0
    outlook_growth = float(np.clip(outlook_growth, -0.5, 0.5))
    return {'model': 'employment_outlook_merged', 'input': {'graduates': graduates, 'employment_lag1': emp_lag1, 'time': time}, 'level_estimate_thousands': round(level_est, 2), 'change_estimate_thousands': round(change_est, 2), 'weights': {'level': round(level_weight, 3), 'change': round(change_weight, 3)}, 'projected_employment_thousands': round(merged_level, 2), 'outlook_growth': round(outlook_growth, 4)}
if __name__ == '__main__':
    print(predict_employment_level(emp_lag1=715.0))
    print(predict_employment_change(graduates=20000, emp_lag1=715.0, time=2022))
    print(merge_employment_models(graduates=20000, emp_lag1=715.0, time=2024))