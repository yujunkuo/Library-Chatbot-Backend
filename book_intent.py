## Book Intent 
import json
import requests as rq
from bs4 import BeautifulSoup

import torch
import numpy as np

from transformers import BertTokenizer
from transformers import BertForTokenClassification


BOOK_MODEL = BertForTokenClassification.from_pretrained("./models/book_model/")
TOKENIZER = BertTokenizer.from_pretrained("bert-base-chinese")


# Public API to get book list
def get_book_list(sentence: str, mysql):
    books, authors = _get_book_and_author(sentence)
    book_info = _get_all_book_info(books, authors, mysql)
    return {"class": "book_list", "book_name": books[0] if books else "", "book_list": book_info}


# (Protected function) Get book name and author name
def _get_book_and_author(sentence: str):
    book_tag_values = ["B-BOOK", "I-AUTHOR", "O", "I-BOOK", "B-AUTHOR", "PAD"]
    tokenized_sentence = TOKENIZER.encode(sentence)
    input_ids = torch.tensor([tokenized_sentence])
    with torch.no_grad():
        output = BOOK_MODEL(input_ids)
    label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
    tokens = TOKENIZER.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
    book, books, author, authors = [], [], [], []
    for i, label_idx in enumerate(label_indices[0]):
        label = book_tag_values[label_idx]
        # Get Book Name
        if label == "B-BOOK":
            if book:
                books.append("".join(book))
                book = []
            book.append(tokens[i])
        elif label == "I-BOOK":
            book.append(tokens[i])
        # Get Author Name
        elif label == "B-AUTHOR":
            if author:
                authors.append("".join(author))
                author = []
            author.append(tokens[i])
        elif label == "I-AUTHOR":
            author.append(tokens[i])
    if book:
        books.append("".join(book))
    if author:
        authors.append("".join(author))
    return (books, authors)


# (Protected function) Get book list information
def _get_all_book_info(books: list, authors: list, mysql):
    cur = mysql.connection.cursor()
    # Only choose the first book and author in the list
    book_name = books[0] if books else None
    author_name = authors[0] if authors else None
    # SQL Statement with book name and author
    if book_name and author_name:
        # First, filter totally identical book name and author
        sql_command = "SELECT DISTINCT title, author, mmsid FROM mms_info WHERE title LIKE %s AND author LIKE %s LIMIT 20;"
        book_name = "%" + book_name + "%"
        author_name = "%" + author_name + "%"
        cur.execute(sql_command, (book_name, author_name))
        fetch_data = cur.fetchall()
        # Then, filter partially identical
        if len(list(fetch_data)) < 20:
            times = int(20-len(list(fetch_data)))
            sql_command = "SELECT DISTINCT title, author, mmsid FROM mms_info WHERE title LIKE %s AND author LIKE %s LIMIT %s;"
            book_name = "%" + "%".join([word for word in book_name[1:-1]]) + "%"
            author_name = "%" + "%".join([word for word in author_name[1:-1]]) + "%"
            cur.execute(sql_command, (book_name, author_name, times))
            fetch_data += cur.fetchall()
        cur.close()
        return fetch_data
    elif book_name:
        # First, filter totally identical book name
        sql_command = "SELECT DISTINCT title, author, mmsid FROM mms_info WHERE title LIKE %s LIMIT 20;"
        book_name = "%" + book_name + "%"
        cur.execute(sql_command, (book_name, ))
        fetch_data = cur.fetchall()
        # Then, filter partially identical
        if len(list(fetch_data)) < 20:
            times = int(20-len(list(fetch_data)))
            sql_command = "SELECT DISTINCT title, author, mmsid FROM mms_info WHERE title LIKE %s LIMIT %s;"
            book_name = "%" + "%".join([word for word in book_name[1:-1]]) + "%"
            cur.execute(sql_command, (book_name, times))
            fetch_data = cur.fetchall()
        cur.close()
        return fetch_data
    elif author_name:
        # First, filter totally identical author
        sql_command = "SELECT DISTINCT title, author, mmsid FROM mms_info WHERE author LIKE %s LIMIT 20;"
        author_name = "%" + author_name + "%"
        cur.execute(sql_command, (author_name, ))
        fetch_data = cur.fetchall()
        # Then, filter partially identical
        if len(list(fetch_data)) < 20:
            times = int(20-len(list(fetch_data)))
            sql_command = "SELECT DISTINCT title, author, mmsid FROM mms_info WHERE author LIKE %s LIMIT %s;"
            author_name = "%" + "%".join([word for word in author_name[1:-1]]) + "%"
            cur.execute(sql_command, (author_name, times))
            fetch_data = cur.fetchall()
        cur.close()
        return fetch_data
    else:
        # Return empty list if no book name or author data is given
        cur.close()
        return []


# Public API to get book info
def get_book_info(mms_id: str, mysql):
    # Send Request with crawler
    url = f"https://nccu.primo.exlibrisgroup.com/primaws/rest/pub/pnxs/L/alma{mms_id}?vid=886NCCU_INST:886NCCU_INST&lang=zh-tw"
    r = rq.get(url).text
    data = json.loads(r)
    # Get Book Name
    if "title" in data["pnx"]["display"] and data["pnx"]["display"]["title"]:
        raw_book_name = data["pnx"]["display"]["title"][0]
        clean_book_name = raw_book_name.split("/")[0].strip() if "/" in raw_book_name else raw_book_name.strip()
    else:
        clean_book_name = "找不到書名資訊"
    # Get Author
    if "creator" in data["pnx"]["display"] and data["pnx"]["display"]["creator"]:
        raw_author = data["pnx"]["display"]["creator"][0]
        clean_author = raw_author.split("$$Q")[0].strip() if "$$Q" in raw_author else raw_author.strip()
    else:
        clean_author = "找不到作者資訊"
    # Get Location and Avalibility
    holding_list = data["delivery"]["holding"]
    location_and_available = []
    for i in range(len(holding_list)):
        location = holding_list[i]["subLocation"]
        available = holding_list[i]["availabilityStatus"]
        location_and_available.append([location, available])
    # Get item-based recommendation from database
    cur = mysql.connection.cursor()
    sql_command = "SELECT mms_top_30 FROM mms_info WHERE mmsid = %s;"
    cur.execute(sql_command, (mms_id, ))
    item_recommendation_mms_id = cur.fetchall()[0][0]
    item_recommendation_list = []
    for curr_mms_id in json.loads(item_recommendation_mms_id)[:10]:
        # print("current mms id: ", curr_mms_id)
        sql_command = "SELECT title FROM mms_info WHERE mmsid = %s;"
        cur.execute(sql_command, (curr_mms_id, ))
        curr_book_name_list = cur.fetchall()
        curr_book_name = curr_book_name_list[0][0][:-2] if curr_book_name_list else ""
        item_recommendation_list.append(curr_book_name + "##" + str(curr_mms_id))
    item_recommendation_res = "@@".join(item_recommendation_list)
    # Get association-based recommendation from database
    sql_command = """
    SELECT item_info.mmsid AS mmsid
    FROM loan_info
    LEFT JOIN item_info
    ON loan_info.iid=item_info.iid
    where uid IN (
    SELECT DISTINCT loan_info.uid
    FROM loan_info
    LEFT JOIN item_info
    ON loan_info.iid=item_info.iid
    where mmsid = %s)
    AND item_info.mmsid != %s
    GROUP BY mmsid
    ORDER BY COUNT(mmsid) DESC
    LIMIT 30;
    """
    cur.execute(sql_command, (mms_id, mms_id, ))
    asso_recommendation_mms_id = cur.fetchall()
    asso_recommendation_list = []
    for curr_mms_id in asso_recommendation_mms_id:
        curr_mms_id = curr_mms_id[0]
        sql_command = "SELECT title FROM mms_info WHERE mmsid = %s;"
        cur.execute(sql_command, (curr_mms_id, ))
        curr_book_name_list = cur.fetchall()
        curr_book_name = curr_book_name_list[0][0][:-2] if curr_book_name_list else ""
        asso_recommendation_list.append(curr_book_name + "##" + str(curr_mms_id))
    asso_recommendation_res = "@@".join(asso_recommendation_list)
    # Get Book Introduction, Cover and HashTag
    sql_command = "SELECT content, cover, hashtag, rating FROM mms_info WHERE mmsid = %s;"
    cur.execute(sql_command, (mms_id, ))
    sql_result = cur.fetchall()
    book_content, book_cover, book_hashtag, book_rating = sql_result[0]
    cur.close()
    # Parsing Hashtag
    book_hashtag_dict = json.loads(book_hashtag) if book_hashtag else dict()
    book_hashtag_list = sorted(book_hashtag_dict.items(), key=lambda x: x[1], reverse=True)
    max_n = 5 if len(book_hashtag_list) > 5 else len(book_hashtag_list)
    max_n_hashtag_list = []
    for k, v in book_hashtag_list[:max_n]:
        max_n_hashtag_list.append(k)
    book_hashtag = max_n_hashtag_list
    # Parse html introduction to clean text introduction
    soup = BeautifulSoup(book_content)
    clean_introduction = "".join(soup.findAll(text=True)).replace(u"\u3000", "").replace("\n", "")
    return {"book_name": clean_book_name, "author": clean_author, "introduction": clean_introduction, "cover": book_cover,
           "hashtag": book_hashtag, "rating": book_rating, "location_and_available": location_and_available,
           "item_recommendation": item_recommendation_res, "asso_recommendation": asso_recommendation_res}

# Public API to get book info
def upload_book_hashtag_and_rating(mms_id: str, input_hashtag: list, input_rating: str, mysql):
    cur = mysql.connection.cursor()
    sql_command = "SELECT hashtag, rating, rating_count FROM mms_info WHERE mmsid = %s;"
    cur.execute(sql_command, (mms_id, ))
    hashtag, rating, rating_count = cur.fetchall()[0]
    cur.close()
    # Handle Hashtag
    hashtag_dict = json.loads(hashtag) if hashtag else dict()
    if input_hashtag:
        for h in input_hashtag:
            if h in hashtag_dict:
                hashtag_dict[h] += 1
            else:
                hashtag_dict[h] = 1
    # Handle rating
    if input_rating:
        input_rating = float(input_rating)
        rating_count += 1
        rating = (rating * rating_count + input_rating) / rating_count 
    # Update Hashtag, rating and rating count
    cur = mysql.connection.cursor()
    sql_command = "UPDATE mms_info SET hashtag = %s, rating = %s, rating_count = %s WHERE mmsid = %s"
    cur.execute(sql_command, (hashtag_dict, rating, rating_count, mms_id, ))
    mysql.connection.commit()
    cur.close()
    # return TODO 1116
    return 
