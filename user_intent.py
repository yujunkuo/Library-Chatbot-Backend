## User Intent

def get_user_based(user_id: str, mysql):
    cur = mysql.connection.cursor()
    sql_command = "SELECT uu_list FROM user_info WHERE uid = %s;"
    cur.execute(sql_command, (user_id, ))
    uu_list = cur.fetchall()[0][0]
    cur.close()
    return {"users": uu_list}

