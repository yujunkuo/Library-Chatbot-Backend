import pandas as pd
import numpy as np
import torch

from flask import Flask
from flask import request
from flask import jsonify

from sentence_transformers import SentenceTransformer
from transformers import BertForSequenceClassification
from transformers import BertForTokenClassification
from transformers import BertTokenizer

from .intent_classifier import IntentClassifier


app = Flask(__name__)


# BOOK_MODEL = BertForTokenClassification.from_pretrained("./book_model/")
# FAQ_MODEL = SentenceTransformer("distiluse-base-multilingual-cased")

# Intent Classifier
INTENT_CLASSIFIER = IntentClassifier()

# ########### FAQ ############
# df = pd.read_csv("./csv_file/faq_data.csv")
# # faqs_dict is Question-Answer's pair
# faqs_dict = dict()
# for k, v in zip(df["問題"], df["答案"]):
#     faqs_dict[k] = v
# faqs = list(faqs_dict.keys())
# faq_embeddings = sbert_model.encode(faqs)

# def calculate_cosine_similarity(x, y):
#     # x = sentence_embeddings[0]
#     # y = sentence_embeddings[1]
#     res = np.dot(x, y) / (np.linalg.norm(x)*np.linalg.norm(y))
#     return res
#     # print("cosine similarity: {:.2f}".format(res))

# def get_most_similar_faq_init(sentence):
#     sentence_embedding = sbert_model.encode(sentence)[0]
#     candidate, candidate_sim = None, -1
#     for faq, faq_embedding in zip(faqs, faq_embeddings):
#         sim = calculate_cosine_similarity(sentence_embedding, faq_embedding)
#         if sim > candidate_sim:
#             candidate_sim = sim
#             candidate = faq
#     # Cosine Similarity Threshold 0.85
#     return (candidate, candidate_sim) if candidate_sim > 0.9 else None

# print(get_most_similar_faq_init("如果我只有兩個人可以借討論室嗎"))
# #################################


# input_sentence = "請問有線性代數的課本嗎"
# pred = get_intent_classification(intent_tokenizer, intent_model, label_map, input_sentence)
# print("The preciction result: {}".format(pred))


@app.route("/", methods=["POST"])
def get_answer():
    data = request.get_json()
    question = data["question"]
    answer = INTENT_CLASSIFIER.get_intent_classification(question)
    return_dict = {"answer": answer}
    return jsonify(return_dict)

if __name__ == "__main__":
    app.run(debug=True, host="140.119.19.18")
