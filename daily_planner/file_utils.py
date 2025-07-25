import json


def read_json(path):
    """
    Read JSON content from a file.

    Args:
        path (str): The path to the JSON file.

    Returns:
        dict: Parsed JSON data.
    """
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write_json(path, data):
    """
    Write dictionary content to a JSON file.

    Args:
        path (str): The file path to write to.
        data (dict): The data to serialize into JSON.
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
