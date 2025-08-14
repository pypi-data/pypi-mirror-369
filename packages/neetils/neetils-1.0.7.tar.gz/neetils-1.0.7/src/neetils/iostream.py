import json
import os
from typing import Union
from tqdm import tqdm
from datasets import load_dataset, Dataset


def read_jsonl(file_path: str, use_tqdm=False):
    with open(file_path, "r") as file:
        if use_tqdm:
            lines = file.readlines()

            file_name = os.path.basename(file_path)
            results = []
            for line in tqdm(lines, desc=file_name):
                results.append(json.loads(line))
            return results
        else:
            return [json.loads(line) for line in file]


def load_jsonl(file_path: str, **kwargs) -> Union[Dataset, list]:
    try:
        dataset = load_dataset("json", data_files=[file_path], **kwargs)["train"]
        return dataset
    except Exception as e:
        print(f"Failed to load JSONL from {file_path} with {e}")
        return read_jsonl(file_path)


def read_json(file_path: str):
    with open(file_path, "r") as file:
        return json.loads(file.read())


def write_jsonl(file_path: str, data_list: list, use_tqdm=False):
    with open(file_path, "w") as file:
        file_name = os.path.basename(file_path)
        for item in tqdm(data_list, desc=file_name, disable=not use_tqdm):
            file.write(json.dumps(item, ensure_ascii=False) + "\n")


def write_json(file_path: str, data_dict: dict):
    with open(file_path, "w") as file:
        file.write(json.dumps(data_dict, ensure_ascii=False))

def read_lines(file_path: str):
    with open(file_path, 'r') as file:
        return [f.strip() for f in file.readlines() if f.strip()]