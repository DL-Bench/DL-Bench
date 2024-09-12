import json

def save_dict_to_jsonl(data_list, file_path):
    """
    Saves a list of dictionaries to a JSON Lines file.

    :param data_list: List of dictionaries to save.
    :param file_path: Path to the JSONL file to save the dictionaries.
    """
    with open(file_path, 'a+') as file:
        json_record = json.dumps(data_list)
        file.write(json_record + '\n')
