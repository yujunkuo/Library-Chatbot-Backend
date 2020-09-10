import time
import yaml

from flask import Flask
from flask import request
from flask import jsonify
from flask_mysqldb import MySQL

from intent_classifier import IntentClassifier
from faq_judge import FAQJudge
from other_intent import OtherIntentHandler
from book_intent import get_book_result


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
INTENT_CLASSIFIER = IntentClassifier()  # Intent Classifier
FAQ_JUDGE = FAQJudge()  # FAQ Judge
OTHER_INTENT_HANDLER = OtherIntentHandler() # Other Intent Handler


def get_answer(sentence: str):
    faq_res = FAQ_JUDGE.get_faq_judge(sentence)
    if faq_res: 
        return {"class": "answer", "answer": faq_res}
    intent_res = INTENT_CLASSIFIER.get_intent_classification(sentence)
    if intent_res == "search_book":
        return get_book_result(sentence, mysql)
    elif intent_res == "borrow_place":
        return {"class": "answer", "answer": "借場地捏"}
    else:
        # return OTHER_INTENT_HANDLER.get_answer(sentence)
        return {"class": "answer", "answer": "其他捏"}

            
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


################## Main Function ##################
def main():
    app.run(debug=True, host=server_config["ip"])


if __name__ == "__main__":
    main()
###################################################
