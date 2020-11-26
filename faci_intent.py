## Facility Intent 

import json
import requests as rq
from bs4 import BeautifulSoup

import torch
import numpy as np
import pandas as pd

from transformers import BertTokenizer
from transformers import BertForTokenClassification
from sentence_transformers import SentenceTransformer


FACI_MODEL = BertForTokenClassification.from_pretrained("./models/faci_model/")
SENTENCE_MODEL = SentenceTransformer("distiluse-base-multilingual-cased")
TOKENIZER = BertTokenizer.from_pretrained("bert-base-chinese")

# Public API to get facility information
def get_faci_info(sentence: str):
    facis = _get_faci_name(sentence)
    faci_info = _get_faci_info(facis)
    faci_info["class"] = "facility"
    return faci_info

# (Protected function) Get facility name
def _get_faci_name(sentence: str):
    faci_tag_values = ["B-FACI", "I-FACI", "O", "PAD"]
    tokenized_sentence = TOKENIZER.encode(sentence)
    input_ids = torch.tensor([tokenized_sentence])
    with torch.no_grad():
        output = FACI_MODEL(input_ids)
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
    faci = facis[0] if facis else "無此場地"
    df = pd.read_csv("./csv_files/faci.csv")
    for idx, val in df.iterrows():
        # Judge whether this entity is in the entities list
        if (faci in val.entity) or (val.entity in faci):
            return {"faci_name": val["entity"], "introduce": val["introduce"], "floor": val["floor"], "number": val["number"], "classify": val["classify(1:設備,2:服務,3:場地,4:館藏資料)"]}
    entity_list_embedding = SENTENCE_MODEL.encode(list(df["entity"]))
    current_embedding = SENTENCE_MODEL.encode(faci)
    candidate, candidate_sim = None, -1
    for entity, entity_embedding in zip(list(df["entity"]), entity_list_embedding):
        sim = _cal_cosine_sim(current_embedding, entity_embedding)
        if sim > candidate_sim:
            candidate_sim, candidate = sim, entity
    # Cosine Similarity Threshold 0.65
    if (candidate is None) or (candidate_sim < 0.65):
        print("設備: ", candidate)
        print("設備相似度: ", candidate_sim)
        return {"faci_name": "", "introduce": "", "floor": "", "number": "", "classify": ""}
    else:
        print("設備相似度: ", candidate_sim)
        val = df[df["entity"] == candidate]
        return {"faci_name": val["entity"].values[0], "introduce": val["introduce"].values[0], "floor": int(val["floor"].values[0]), "number": int(val["number"].values[0]), "classify": int(val["classify(1:設備,2:服務,3:場地,4:館藏資料)"].values[0])}

# (Protected function) Calculate Cosine Similarity between to sentences
def _cal_cosine_sim(x, y):
    res = np.dot(x, y) / (np.linalg.norm(x)*np.linalg.norm(y))
    return res
