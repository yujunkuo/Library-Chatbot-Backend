import time
import torch
import numpy as np

from flask import Flask
from flask import request
from flask import jsonify

from transformers import BertForTokenClassification
from transformers import BertTokenizer

from intent_classifier import IntentClassifier
from faq_judge import FAQJudge
from other_intent import OtherIntentHandler


app = Flask(__name__)


BOOK_MODEL = BertForTokenClassification.from_pretrained("./models/book_model/")
TOKENIZER = BertTokenizer.from_pretrained("bert-base-chinese")

# Global Variables (Handlers)
INTENT_CLASSIFIER = IntentClassifier()  # Intent Classifier
FAQ_JUDGE = FAQJudge()  # FAQ Judge
OTHER_INTENT_HANDLER = OtherIntentHandler() # Other Intent Handler

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
        return OTHER_INTENT_HANDLER.get_answer()

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
    if target:
        targets.append("".join(target))
    return ", ".join(targets) if targets else "找不到書名"

            
@app.route("/api/v1/", methods=["POST"])
def home():
    data = request.get_json()
    sentence = data["question"]
    start_time = time.time()
    answer = get_answer(sentence)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict = {"answer": answer, "handle_time": handle_time}
    return jsonify(return_dict)

def main():
    app.run(debug=True, host="140.119.19.18")


if __name__ == "__main__":
    main()
    