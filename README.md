# API Documentation

## Book List API

> Returns json data about the book searching result of the question.

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

## Single Book Information API

> Returns json data about the detail information of the single book.

* **URL**

  http://140.119.19.18:5000/api/v1/book/

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**

  `"mms_id"=[str]`
  
  `"session_id"=[str]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
    "asso_recommendation": "暮光之城##991019585029705721@@時間之砂##991009612479705721@@暮光之城 : 破曉##991020775469705721@@暮光之城 : 新月##991019540129705721",
    "author": "麥爾 (Meyer, Stephenie)",
    "book_name": "暮光之城 : 蝕",
    "cover": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/042/48/0010424899.jpg&v=4963250a&w=348&h=348",
    "handle_time": 1.32,
    "hashtag": [],
    "introduction": "有三件事我很確定： 第一、愛德華是吸血鬼 第二、出於天性，他渴望喝我的血 第三、我無可救藥地愛上他了……",
    "item_recommendation": "暮光之城 : 破曉##991020775469705721@@暮光之城 : 新月##991019540129705721@@暮光之城##991019585029705721@@新郎##991016175879705721",
    "location_and_available": [
        [
            "總圖三樓中文圖書區(藍標)",
            "available"
        ]
    ],
    "rating": null,
    "session_id": "abc123"
}`
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/book/",
      data: {"mms_id": "991019804019705721", "session_id": "abc123"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```

## Upload Book's Hashtag and Rating API

> Returns json data about the handle time.

* **URL**

  http://140.119.19.18:5000/api/v1/book_upload/

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**

  `"mms_id"=[str]`
  
  `"session_id"=[str]`
  
  `"hashtag"=[array]`
  
  `"rating"=[str]`
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
    "asso_recommendation": "暮光之城##991019585029705721@@時間之砂##991009612479705721@@暮光之城 : 破曉##991020775469705721@@暮光之城 : 新月##991019540129705721",
    "author": "麥爾 (Meyer, Stephenie)",
    "book_name": "暮光之城 : 蝕",
    "cover": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/042/48/0010424899.jpg&v=4963250a&w=348&h=348",
    "handle_time": 1.32,
    "hashtag": [],
    "introduction": "有三件事我很確定： 第一、愛德華是吸血鬼 第二、出於天性，他渴望喝我的血 第三、我無可救藥地愛上他了……",
    "item_recommendation": "暮光之城 : 破曉##991020775469705721@@暮光之城 : 新月##991019540129705721@@暮光之城##991019585029705721@@新郎##991016175879705721",
    "location_and_available": [
        [
            "總圖三樓中文圖書區(藍標)",
            "available"
        ]
    ],
    "rating": null,
    "session_id": "abc123"
}`
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/book/",
      data: {"mms_id": "991019804019705721", "session_id": "abc123"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```
