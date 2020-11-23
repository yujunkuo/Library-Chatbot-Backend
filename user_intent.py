## User Intent

import json
from datetime import datetime

def get_user_recommendation(user_id: str, mysql):
    # Get user-based recommendation from database
    cur = mysql.connection.cursor()
    sql_command = "SELECT uu_list FROM user_info WHERE uid = %s;"
    cur.execute(sql_command, (user_id, ))
    user_recommendation_mms_id = cur.fetchall()[0][0]
    user_recommendation_list = []
    for curr_mms_id in json.loads(user_recommendation_mms_id)[:10]:
        sql_command = "SELECT title FROM mms_info WHERE mmsid = %s;"
        cur.execute(sql_command, (curr_mms_id, ))
        curr_book_name_list = cur.fetchall()
        curr_book_name = curr_book_name_list[0][0][:-2] if curr_book_name_list else ""
        user_recommendation_list.append(curr_book_name + "##" + str(curr_mms_id))
    user_recommendation_res = "@@".join(user_recommendation_list)
    return {"user_recommendation": user_recommendation_res}

def upload_browsing_history(user_id, mms_id, start_time, end_time, mysql):
    date_format = "%Y-%m-%d %H:%M:%S"
    start_time = datetime.strptime(start_time, date_format)
    end_time = datetime.strptime(end_time, date_format)
    df_time = end_time - start_time
    df_time_in_seconds = df_time.total_seconds()
    # Fetch old browsing history
    cur = mysql.connection.cursor()
    sql_command = "SELECT activity_logs FROM user_info WHERE uid = %s;"
    cur.execute(sql_command, (user_id, ))
    history = cur.fetchall()[0][0]
    cur.close()
    # Update new browsing history
    history = json.loads(history) if history else dict()
    if mms_id in history:
        history[mms_id] += df_time_in_seconds
    else:
        history[mms_id] = df_time_in_seconds
    cur = mysql.connection.cursor()
    sql_command = "UPDATE user_info SET activity_logs = %s WHERE uid = %s"
    cur.execute(sql_command, (history, user_id, ))
    mysql.connection.commit()
    cur.close()
    return {"res": "success"}
