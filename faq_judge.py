## FAQ Judge class

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

class FAQJudge:

    def __init__(self):
        self._model = SentenceTransformer("distiluse-base-multilingual-cased")
        self._df = pd.read_csv("./csv_files/faq_data_1117.csv")
        # faqs_dict is Question-Answer's pair
        self._faqs_dict = dict()
        for k, v in zip(self._df["問題"], self._df["答案"]):
            self._faqs_dict[k] = v
        self._faqs = list(self._faqs_dict.keys())
        self._faq_embeddings = self._model.encode(self._faqs)
    
    # (Public function) This is the API for FAQ Judgement
    def get_faq_judge(self, sentence: str):
        sentence_embedding = self._model.encode(sentence)
        candidate, candidate_sim = None, -1
        for faq, faq_embedding in zip(self._faqs, self._faq_embeddings):
            sim = self._cal_cosine_sim(sentence_embedding, faq_embedding)
            if sim > candidate_sim:
                candidate_sim, candidate = sim, faq
        # Cosine Similarity Threshold 0.85
        if (candidate is None) or (candidate_sim < 0.85):
            print("常見問答相似度: ", candidate_sim)
            return None
        else:
            print("常見問答相似度: ", candidate_sim)
            answer = self._faqs_dict[candidate]
            return answer

    # (Protected function) Calculate Cosine Similarity between to sentences
    def _cal_cosine_sim(self, x, y):
        res = np.dot(x, y) / (np.linalg.norm(x)*np.linalg.norm(y))
        return res
