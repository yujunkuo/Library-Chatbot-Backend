## Facility Intent 

import json
import requests as rq
from bs4 import BeautifulSoup

import torch
import numpy as np
import pandas as pd

from transformers import BertTokenizer
from transformers import BertForTokenClassification


FACI_MODEL = BertForTokenClassification.from_pretrained("./models/faci_model/")
TOKENIZER = BertTokenizer.from_pretrained("bert-base-chinese")


# Public API to get facility information
def get_faci_info(sentence: str):
    facis = _get_faci_name(sentence)
    faci_info = _get_faci_info(facis)
    return faci_info


# (Protected function) Get facility name
def _get_faci_name(sentence: str):
    faci_tag_values = ["B-FACI", "I-FACI", "O", "PAD"]
    tokenized_sentence = TOKENIZER.encode(sentence)
    input_ids = torch.tensor([tokenized_sentence])
    with torch.no_grad():
        output = BOOK_MODEL(input_ids)
    label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
    tokens = TOKENIZER.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
    faci, facis = [], []
    for i, label_idx in enumerate(label_indices[0]):
        label = faci_tag_values[label_idx]
        # Get Facility Name
        if label == "B-FACI":
            if faci:
                facis.append("".join(faci))
                faci = []
            faci.append(tokens[i])
        elif label == "I-FACI":
            faci.append(tokens[i])
    if faci:
        facis.append("".join(faci))
    return facis

# (Protected function) Get facility information
def _get_faci_info(facis):
    faci = facis[0]
    df = pd.read_csv("./csv_files/faci.csv")
    for idx, val in df.iterrows():
        if (faci in val.entity) or (val.entity in faci):
            return {"faci_name": faci, "introduction": val["introduction"], "floor": val["floor"], "number": val["number"], "classify": val["classify(1:設備,2:服務,3:場地,4:館藏資料)"]}
    return {"faci_name": "", "introduction": "", "floor": "", "number": "", "classify": ""}
