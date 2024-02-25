def is_valid_integer(value):
    return str(value).isdigit()


def is_valid_string(value):
    return isinstance(value, str) and value.strip() != ""


def is_valid_test_case_data(data):
    if not isinstance(data, dict):
        return False

    if "name" not in data or not is_valid_string(data["name"]):
        return False

    if "description" in data and not is_valid_string(data["description"]):
        return False

    return True


def is_valid_execution_data(data):
    if not isinstance(data, dict):
        return False

    test_case_id = data.get("test_case_id")
    result = data.get("result")

    if not test_case_id or not result:
        return False

    if not is_valid_integer(test_case_id):
        return False

    if not is_valid_string(result):
        return False

    return True
