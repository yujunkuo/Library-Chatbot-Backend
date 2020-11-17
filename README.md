# API Documentation

## Book List API

> Returns json data about the book searching result of the question

* **URL**

  http://140.119.19.18:5000/api/v1/book_list/

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**

  `"question"=[str]`
  
  `"session_id"=[str]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ "class": "book_list", "book_name": "暮光之城", "handle_time": 12.74, "session_id": "abc123", "book_list": [
                      [
                          "暮光之城. 布莉的重生",
                          "麥爾 (Meyer, Stephenie)",
                          991005224129705721
                      ],
                      [
                          "暮光之城 : 新月",
                          "麥爾 (Meyer, Stephenie)",
                          991019540129705721
                      ]
                    ] 
                  }`
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/book_list/",
      data: {"question": "暮光之城這本書有在圖書館嗎", "session_id": "abc123"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```
