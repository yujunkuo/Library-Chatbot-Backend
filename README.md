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
    **Content:** `{"session_id": "abc123", "handle_time": 12.74, "class": "book_list", "book_name": "暮光之城", "book_list": [
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
    "session_id": "abc123",
    "handle_time": 1.32,
    "book_name": "暮光之城 : 蝕",
    "author": "麥爾 (Meyer, Stephenie)",
    "introduction": "有三件事我很確定： 第一、愛德華是吸血鬼 第二、出於天性，他渴望喝我的血 第三、我無可救藥地愛上他了……",
    "cover": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/042/48/0010424899.jpg&v=4963250a&w=348&h=348",
    "location_and_available": [
        [
            "總圖三樓中文圖書區(藍標)",
            "available"
        ]
    ],
    "hashtag": [],
    "rating": null,
    "item_recommendation": "暮光之城 : 破曉##991020775469705721@@暮光之城 : 新月##991019540129705721@@暮光之城##991019585029705721@@新郎##991016175879705721",
    "asso_recommendation": "暮光之城##991019585029705721@@時間之砂##991009612479705721@@暮光之城 : 破曉##991020775469705721@@暮光之城 : 新月##991019540129705721"
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

## Upload Book's Hashtag and Rating API (# TODO 2020-11-17 Can't upload Chinese Hashtag Bug)

> Returns json data about the handle time.

* **URL**

  http://140.119.19.18:5000/api/v1/book_upload/

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**

  `"mms_id"=[str]`
  
  `"hashtag"=[str]`
  
  `"rating"=[str]`
  
  `"session_id"=[str]`
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
    "session_id": "abc123",
    "handle_time": 3.68
}`
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/book_upload/",
      data: {"mms_id": "991019804019705721", "hashtag": "["好看", "懸疑"]", "rating": "3", "session_id": "abc123"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```
  
## Get Calendar of Recent Library Events

> Returns json data about the library events in two weeks.

* **URL**

  http://140.119.19.18:5000/api/v1/calendar/

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**
  
  `"day"=[str]`
  
  `"session_id"=[str]`
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
    "session_id": "abc123",
    "handle_time": 1.3,
    "current_date": "2020-11-17",
    "first_week_calendar": [
        [
            "2020-11-16",
            "2020-11-17",
            "2020-11-18",
            "2020-11-19",
            "2020-11-20",
            "2020-11-21",
            "2020-11-22"
        ],
        [
            [
                "2020-11-16",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ],
            [
                "2020-11-16",
                "上午8點",
                "",
                "資訊教室例行維護不開放"
            ]
        ],
        [
            [
                "2020-11-17",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-18",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-19",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-20",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-21",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-22",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ]
    ],
    "second_week_calendar": [
        [
            "2020-11-23",
            "2020-11-24",
            "2020-11-25",
            "2020-11-26",
            "2020-11-27",
            "2020-11-28",
            "2020-11-29"
        ],
        [
            [
                "2020-11-23",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-24",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-25",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-26",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-27",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-28",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ],
        [
            [
                "2020-11-29",
                "7 days",
                "展覽",
                "走畫文山畫展"
            ]
        ]
    ]
}`
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/calendar/",
      data: {"day": "7", "session_id": "abc123"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```

## Get Library Facility API

> Returns json data about the detail information of the facility.

* **URL**

  http://140.119.19.18:5000/api/v1/facility/

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**
  
  `"question"=[str]`
  
  `"session_id"=[str]`
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
    "session_id": "abc123",
    "handle_time": 0.28,
    "class": "facility",
    "faci_name": "討論室",
    "classify": 3,
    "number": 4,
    "floor": 7,
    "introduce": "(可放預約連結)七樓討論室包括五間3~6人討論室、兩間24人專題研討室，分別配置壁掛或移動式螢幕、白板，透過場地管理系統預約登記，現場在報到機刷卡後使用，至少需要3張有效借書證。"
}`
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/facility/",
      data: {"question": "討論室在幾樓", "session_id": "abc123"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```
  
## Other Question API (#TODO 2020-11-17 Not Yet Finished)

> Returns json data about the answer of the question.

* **URL**

  http://140.119.19.18:5000/api/v1/other/

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**
  
  `"question"=[str]`
  
  `"session_id"=[str]`
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{
    "session_id": "abc123",
    "handle_time": 0.16,
    "class": "answer",
    "answer": "其他捏"
}`
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/other/",
      data: {"question": "討論室在幾樓", "session_id": "abc123"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```

## User-based recommendation API (#TODO 2020-11-17 Not Yet Finished)

> Returns json data about the user-based recommendation.

* **URL**

  Not Yet

* **Method:**

  `POST`
  
*  **URL Params**
 
   None

* **Data Params**
  
  Not Yet
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** Not Yet
 
* **Error Response:**

  * **Code:** 4XX ERROR CODE <br />

* **Sample Call:**

  Not Yet
