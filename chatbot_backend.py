from flask import Flask, request, jsonify
from transformers import BertForSequenceClassification, BertForTokenClassification
import torch

app = Flask(__name__)


INTENT_MODEL = BertForSequenceClassification.from_pretrained("./intent_model/")
BOOK_MODEL = BertForTokenClassification.from_pretrained("./book_model/")

@app.route("/", methods=["POST"])
def home():
    return_dict = {"response_text": "hello"}
    return jsonify(return_dict)

if __name__ == "__main__":
    app.run(debug=True, host="140.119.19.18")