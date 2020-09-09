import time
import torch
import yaml
import numpy as np

from flask import Flask
from flask import request
from flask import jsonify
from flask_mysqldb import MySQL

from transformers import BertForTokenClassification
from transformers import BertTokenizer

from intent_classifier import IntentClassifier
from faq_judge import FAQJudge
from other_intent import OtherIntentHandler


# Construct App
app = Flask(__name__)


# Read MySQL Config
with open("./config/database.yml", 'r') as stream:
    try:
        mysql_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


# Set MySQL Config
app.config["MYSQL_HOST"] = mysql_config["host"]
app.config["MYSQL_USER"] = mysql_config["username"]
app.config["MYSQL_PASSWORD"] = mysql_config["password"]
app.config["MYSQL_DB"] = mysql_config["database"]


# Construct MySQL Object
mysql = MySQL(app)


# Read Server Config
with open("./config/server.yml", 'r') as stream:
    try:
        server_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


BOOK_MODEL = BertForTokenClassification.from_pretrained("./models/book_model/")
TOKENIZER = BertTokenizer.from_pretrained("bert-base-chinese")


# Global Variables (Handlers)
INTENT_CLASSIFIER = IntentClassifier()  # Intent Classifier
FAQ_JUDGE = FAQJudge()  # FAQ Judge
OTHER_INTENT_HANDLER = OtherIntentHandler() # Other Intent Handler


def get_answer(sentence: str):
    faq_res = FAQ_JUDGE.get_faq_judge(sentence)
    if faq_res: 
        return {"class": "answer", "answer": faq_res}
    intent_res = INTENT_CLASSIFIER.get_intent_classification(sentence)
    if intent_res == "search_book":
        book_name = _get_book_name(sentence)
        book_info = _get_all_book_info(book_name)
        return {"class": "book_list", "book_name": book_name, "book_list": book_info}
    elif intent_res == "borrow_place":
        return {"class": "answer", "answer": "借場地捏"}
    else:
        # return OTHER_INTENT_HANDLER.get_answer(sentence)
        return {"class": "answer", "answer": "其他捏"}


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

def _get_all_book_info(book_name: str):
    cur = mysql.connection.cursor()
    sql_command = "SELECT DISTINCT `Title (Complete)`, Author, `MMS Id` FROM p9 WHERE `Title (Complete)` LIKE %s;"
    book_name = "%" + book_name + "%"
    cur.execute(sql_command, (book_name, ))
    fetch_data = cur.fetchall()
    cur.close()
    return fetch_data

            
@app.route("/api/v1/", methods=["POST"])
def home():
    data = request.get_json()
    sentence = data["question"]
    id = data["id"]
    start_time = time.time()
    return_dict = get_answer(sentence)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["id"] = id
    return jsonify(return_dict)

# 書名\作者\圖書館位置\有沒有在館藏


def main():
    app.run(debug=True, host=server_config["ip"])


if __name__ == "__main__":
    main()
    
