import numpy as np

# Model 1: Employment Level
M1_COEF         = np.array([1450.92095196])
M1_INTERCEPT    = 722.1839917936694
M1_SCALER_MEAN  = np.array([715.47249707])
M1_SCALER_SCALE = np.array([1438.31352529])

# Model 2: Employment Change
M2_COEF         = np.array([-0.59461836, -0.8840954, 13.16175616])
M2_INTERCEPT    = 1205.768485392164
M2_SCALER_MEAN  = np.array([20188.04279015, 715.47249707])
M2_SCALER_SCALE = np.array([37549.96159868, 1438.31352529])


def predict_employment_level(emp_lag1: float) -> dict:
    x = np.array([[emp_lag1]])
    x_scaled = (x - M1_SCALER_MEAN) / M1_SCALER_SCALE
    prediction = (x_scaled @ M1_COEF + M1_INTERCEPT).item()
    return {
        "model": "employment_level",
        "input": {"employment_lag1": emp_lag1},
        "predicted_employment_thousands": round(prediction, 2),
    }


def predict_employment_change(graduates: float, emp_lag1: float, time: int) -> dict:
    x_to_scale = np.array([[graduates, emp_lag1]])
    x_scaled   = (x_to_scale - M2_SCALER_MEAN) / M2_SCALER_SCALE
    x_full     = np.array([[float(time), x_scaled[0, 0], x_scaled[0, 1]]])
    prediction = (x_full @ M2_COEF + M2_INTERCEPT).item()
    return {
        "model": "employment_change",
        "input": {
            "graduates": graduates,
            "employment_lag1": emp_lag1,
            "time": time,
        },
        "predicted_change_thousands": round(prediction, 2),
    }


if __name__ == "__main__":
    print(predict_employment_level(emp_lag1=715.0))
    print(predict_employment_change(graduates=20000, emp_lag1=715.0, time=2022))