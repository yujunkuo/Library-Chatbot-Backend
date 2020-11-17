## User Intent

import json

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

    

