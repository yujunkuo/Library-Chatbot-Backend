import time
import yaml
import datetime

from flask import Flask
from flask import request
from flask import jsonify
from flask_mysqldb import MySQL

import book_intent
import other_intent
import faci_intent
import user_intent
import faq_judge
import intent_classifier
import calendar_crawler


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
# INTENT_CLASSIFIER = intent_classifier.IntentClassifier()  # Intent Classifier
FAQ_JUDGE = faq_judge.FAQJudge()  # FAQ Judge
# OTHER_INTENT_HANDLER = other_intent.OtherIntentHandler()  # Other Intent Handler


def get_answer(sentence: str):
    faq_res = FAQ_JUDGE.get_faq_judge(sentence)
    if faq_res: 
        return {"class": "answer", "answer": faq_res}
    else:
        return {"class": "answer", "answer": "抱歉我還在學習中，請洽詢館員唷"}
    # intent_res = INTENT_CLASSIFIER.get_intent_classification(sentence)
    # if intent_res == "search_book":
    #     return book_intent.get_book_list(sentence, mysql)
    # elif intent_res == "borrow_place":
    #     return {"class": "answer", "answer": "借場地捏"}
    # else:
    #     # return OTHER_INTENT_HANDLER.get_answer(sentence)
    #     return {"class": "answer", "answer": "其他捏"}


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

# Upload Book Hashtag and Rating API
@app.route("/api/v1/book_upload/", methods=["POST"])
def book_upload_api():
    data = request.get_json()
    mms_id = data["mms_id"]
    session_id = data["session_id"]
    input_hashtag = data["hashtag"]
    input_rating = data["rating"]
    start_time = time.time()
    book_intent.upload_book_hashtag_and_rating(mms_id, input_hashtag, input_rating, mysql)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict = {}
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)

# Get Google Calendar API
@app.route("/api/v1/calendar/", methods=["POST"])
def calendar_api():
    data = request.get_json()
    session_id = data["session_id"]
    day = data["day"]
    start_time = time.time()
    first_week_calendar = calendar_crawler.get_current_week_calendar(int(day))
    second_week_calendar = calendar_crawler.get_current_week_calendar(int(day)+7)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict = dict()
    return_dict["first_week_calendar"] = first_week_calendar
    return_dict["second_week_calendar"] = second_week_calendar
    return_dict["current_date"] = str(datetime.date.today())
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)

# Get Facility API
@app.route("/api/v1/facility/", methods=["POST"])
def faci_api():
    data = request.get_json()
    sentence = data["question"]
    session_id = data["session_id"]
    start_time = time.time()
    return_dict = faci_intent.get_faci_info(sentence)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)

# Get User-based Recommendation API
@app.route("/api/v1/user_recommendation/", methods=["POST"])
def user_recommendation_api():
    data = request.get_json()
    user_id = data["user_id"]
    session_id = data["session_id"]
    start_time = time.time()
    return_dict = user_intent.get_user_recommendation(user_id, mysql)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["user_id"] = user_id
    return_dict["session_id"] = session_id
    return jsonify(return_dict)

# Get Top 10 Books API
@app.route("/api/v1/book_top_ten/", methods=["POST"])
def book_top_ten_api():
    data = request.get_json()
    session_id = data["session_id"]
    start_time = time.time()
    return_dict = book_intent.get_book_top_ten(mysql)
    end_time = time.time()
    handle_time = round(end_time - start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)

# Upload Browsing History API
@app.route("/api/v1/browsing_upload/", methods=["POST"])
def browsing_upload_api():
    data = request.get_json()
    session_id = data["session_id"]
    user_id = data["user_id"]
    mms_id = data["mms_id"]
    start_time = data["start_time"]
    end_time = data["end_time"]
    x_start_time = time.time()
    return_dict = user_intent.upload_browsing_history(user_id, mms_id, start_time, end_time, mysql)
    x_end_time = time.time()
    handle_time = round(x_end_time - x_start_time, 2)
    return_dict["handle_time"] = handle_time
    return_dict["session_id"] = session_id
    return jsonify(return_dict)


################## Main Function ##################
def main():
    app.run(debug=True, host=server_config["ip"], port=5000)

if __name__ == "__main__":
    main()
###################################################
