import time
import yaml

from flask import Flask
from flask import request
from flask import jsonify
from flask_mysqldb import MySQL

import book_intent
import other_intent
import faq_judge
import intent_classifier


######### Construct App and Server Config #########
# construct App
app = Flask(__name__)

# Read Server Config
with open("./config/server.yml", 'r') as stream:
    try:
        server_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
###################################################


################## Mysql setting ##################
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
###################################################


# Global Variables (Handlers)
INTENT_CLASSIFIER = intent_classifier.IntentClassifier()  # Intent Classifier
FAQ_JUDGE = faq_judge.FAQJudge()  # FAQ Judge
OTHER_INTENT_HANDLER = other_intent.OtherIntentHandler()  # Other Intent Handler


def get_answer(sentence: str):
    faq_res = FAQ_JUDGE.get_faq_judge(sentence)
    if faq_res: 
        return {"class": "answer", "answer": faq_res}
    intent_res = INTENT_CLASSIFIER.get_intent_classification(sentence)
    if intent_res == "search_book":
        return book_intent.get_book_list(sentence, mysql)
    elif intent_res == "borrow_place":
        return {"class": "answer", "answer": "借場地捏"}
    else:
        # return OTHER_INTENT_HANDLER.get_answer(sentence)
        return {"class": "answer", "answer": "其他捏"}


# Other Question API          
@app.route("/api/v1/other/", methods=["POST"])
def other_api():
    data = request.get_json()
    sentence = data["question"]
    session_id = data["session_id"]
    start_time = time.time()
    return_dict = get_answer(sentence)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)


# Search Book API
@app.route("/api/v1/book_list/", methods=["POST"])
def book_list_api():
    data = request.get_json()
    sentence = data["question"]
    session_id = data["session_id"]
    start_time = time.time()
    return_dict = book_intent.get_book_list(sentence, mysql)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)

# Get Book Information API
@app.route("/api/v1/book/", methods=["POST"])
def book_api():
    data = request.get_json()
    mms_id = data["mms_id"]
    session_id = data["session_id"]
    start_time = time.time()
    return_dict = book_intent.get_book_info(mms_id, mysql)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)

################## Main Function ##################
def main():
    app.run(debug=True, host=server_config["ip"], port=5000)

if __name__ == "__main__":
    main()
###################################################
