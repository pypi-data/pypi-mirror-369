import os
import json
import pandas as pd
import numpy as np

def read_any(path):
    if path.endswith('.json'):
        with open(path, 'r') as f:
            data = json.load(f)
    if path.endswith('.jsonl'):
        with open(path, 'r') as f:
            data = [json.loads(line.strip()) for line in f]
    if path.endswith('.parquet'):
        df = pd.read_parquet(path)
        df = df.map(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
        data = df.to_dict(orient='records')
    if path.endswith('.csv'):
        df = pd.read_csv(path)
        data = df.to_dict(orient='records')
    return data

def save_jsonl(datas, save_path, exist_ok=True):
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists(save_path) and not exist_ok:
        raise("file existed")
    with open(save_path, 'w', encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

def save_parquet(datas, save_path, exist_ok=True):
    from datasets import load_dataset, Dataset
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists(save_path) and not exist_ok:
        raise("file existed")
    dataset = Dataset.from_list(datas)
    dataset.to_parquet(save_path)
