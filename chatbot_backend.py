import numpy as np
import torch

from flask import Flask
from flask import request
from flask import jsonify

from transformers import BertForTokenClassification
from transformers import BertTokenizer

from intent_classifier import IntentClassifier
from faq_judge import FAQJudge


app = Flask(__name__)


BOOK_MODEL = BertForTokenClassification.from_pretrained("./models/book_model/")
TOKENIZER = BertTokenizer.from_pretrained("bert-base-chinese")

INTENT_CLASSIFIER = IntentClassifier()  # Intent Classifier
FAQ_JUDGE = FAQ_JUDGE()  # FAQ Judge

def get_answer(sentence: str):
    faq_res = FAQ_JUDGE.get_faq_judge(sentence)
    if faq_res: 
        return faq_res
    intent_res = INTENT_CLASSIFIER.get_intent_classification(sentence)
    if intent_res == "search_book":
        return _get_book_name(sentence)
    elif intent_res == "borrow_place":
        return "借場地嗎?"
    else:
        return "其他問題嗎?"

def _get_book_name(sentence: str):
    book_tag_values = ["I-BOOK", "O", "B-BOOK", "PAD"]
    tokenized_sentence = TOKENIZER.encode(sentence)
    input_ids = torch.tensor([tokenized_sentence])
    with torch.no_grad():
        output = BOOK_MODEL(input_ids)
    label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
    tokens = TOKENIZER.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
    target, targets = [], []
    for i, label_idx in enumerate(label_indices[0]):
        label = book_tag_values[label_idx]
        if label == "B-BOOK":
            if target:
                targets.append("".join(target))
                target = []
            target.append(tokens[i])
        elif label == "I-BOOK":
            target.append(tokens[i])
    return targets[0]

            
@app.route("/", methods=["POST"])
def home():
    data = request.get_json()
    sentence = data["question"]
    answer = get_answer(sentence)
    return_dict = {"answer": answer}
    return jsonify(return_dict)

if __name__ == "__main__":
    app.run(debug=True, host="140.119.19.18")
