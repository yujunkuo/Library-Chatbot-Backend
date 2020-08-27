# Library-Chatbot-Backend

## API Documentation

### Get Chatbot's Response & Answer
----
  Returns json data about the answer of the question and the processing time.

* **URL**

  http://140.119.19.18:5000/api/v1/

* **Method:**

  `POST`
  
*  **URL Params**

   **Required:**
 
   None

* **Data Params**

  `"question"=[str]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ "answer" : "館藏中沒有此書籍", "handle_time" : 0.12 }`
 
* **Error Response:**

  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** `{ "error" : "未被授權進行此操作" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      type : "POST",
      url: "http://140.119.19.18:5000/api/v1/",
      data: {"question": "我想找老人與海這本書"}
      dataType: "json", 
      success : function(r) {
        console.log(r);
      }
    });
  ```
