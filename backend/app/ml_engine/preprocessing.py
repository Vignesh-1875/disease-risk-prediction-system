FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]

RANGES = {
    "age": (18, 120),
    "sex": (0, 1),
    "cp": (0, 3),
    "trestbps": (70, 250),
    "chol": (50, 700),
    "fbs": (0, 1),
    "restecg": (0, 2),
    "thalach": (40, 250),
    "exang": (0, 1),
    "oldpeak": (0, 10),
    "slope": (0, 2),
    "ca": (0, 3),
    "thal": (0, 3),
}


def validate_input(data):
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    values = {}
    for feature in FEATURES:
        if feature not in data:
            raise ValueError(f"Missing required field: {feature}")
        try:
            values[feature] = float(data[feature])
        except (TypeError, ValueError):
            raise ValueError(f"{feature} must be numeric") from None
        low, high = RANGES[feature]
        if not low <= values[feature] <= high:
            raise ValueError(f"{feature} must be between {low} and {high}")
        if feature not in {"oldpeak"} and values[feature] != int(values[feature]):
            raise ValueError(f"{feature} must be an integer")
        if feature != "oldpeak":
            values[feature] = int(values[feature])
    return values


def to_vector(values):
    return [[values[feature] for feature in FEATURES]]