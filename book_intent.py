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
    return {"class": "book_list", "book_name": book_name, "book_list": book_info}


# (Protected function) Get book name and author name
def _get_book_and_author(sentence: str):
    book_tag_values = ["I-BOOK", "O", "B-BOOK", "PAD"]
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
    book_name = books[0] if books else None
    author_name = authors[0] if authors else None
    if book_name and author_name:
        # TODO 1022 -- Determine appropriate SQL command with different status
        # TODO 1022 -- Retrieve new version of Entity Recognition Model to the server
        sql_command = "SELECT DISTINCT `Title (Complete)`, Author, `MMS Id` FROM p9 WHERE `Title (Complete)` LIKE %s;"
        book_name = "%" + book_name + "%"
        cur.execute(sql_command, (book_name, ))
        fetch_data = cur.fetchall()
        cur.close()
    return fetch_data


# Public API to get book info
def get_book_info(mms_id: int):
    # Send Request
    url = f"https://nccu.primo.exlibrisgroup.com/primaws/rest/pub/pnxs/L/alma{mms_id}?vid=886NCCU_INST:886NCCU_INST&lang=zh-tw"
    r = rq.get(url).text
    data = json.loads(r)
    # Get Book Name
    raw_book_name = data["pnx"]["display"]["title"][0]
    clean_book_name = raw_book_name.split("/")[0].strip() if "/" in raw_book_name else raw_book_name.strip()
    # Get Author
    raw_author = data["pnx"]["display"]["creator"][0]
    clean_author = raw_author.split("$$Q")[0].strip() if "$$Q" in raw_author else raw_author.strip()
    # Get Location and Avalibility
    holding_list = data["delivery"]["holding"]
    location_and_available = []
    for i in range(len(holding_list)):
        location = holding_list[i]["subLocation"]
        available = holding_list[i]["availabilityStatus"]
        location_and_available.append([location, available])
    return{"book_name": clean_book_name, "author": clean_author, "location_and_available": location_and_available}
