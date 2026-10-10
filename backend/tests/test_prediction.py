import pytest

from app.ml_engine.preprocessing import validate_input


VALID_INPUT = {
    "age": 45, "sex": 1, "cp": 2, "trestbps": 130, "chol": 240,
    "fbs": 0, "restecg": 0, "thalach": 150, "exang": 0,
    "oldpeak": 1.2, "slope": 1, "ca": 0, "thal": 2,
}


def test_valid_input_is_normalized():
    assert validate_input(VALID_INPUT)["oldpeak"] == 1.2


@pytest.mark.parametrize("field,value", [("age", 17), ("chol", 701), ("cp", 4)])
def test_invalid_ranges_are_rejected(field, value):
    data = {**VALID_INPUT, field: value}
    with pytest.raises(ValueError):
        validate_input(data)


def test_missing_input_is_rejected():
    with pytest.raises(ValueError):
        validate_input({})