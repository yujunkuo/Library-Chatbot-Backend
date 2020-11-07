import datetime
import requests as rq
from bs4 import BeautifulSoup


def get_current_week_calendar(input_day: int = 0):

    # 結果
    result = [[] for _ in range(7)]

    # 取得日期 (今天 + input_day)
    curr_date = datetime.date.today() + datetime.timedelta(days=input_day)

    # 爬圖書館行事曆
    start_date = str(curr_date).replace("-", "")
    end_date = str(curr_date + datetime.timedelta(days=31)).replace("-", "")
    date_range = f"{start_date}/{end_date}"
    url = f"https://calendar.google.com/calendar/u/0/htmlembed?height=600&wkst=2&bgcolor=%23ffffff&ctz=Asia/Taipei&src=bmNjdWRobEBnbWFpbC5jb20&src=ZjU2OGdjc3NtcmNudnVvOW92ZzJqMXZ2cG9AZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&src=dGYwbDc5c2pxNzA4dTF1NmF1NWdobzNhM29AZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&src=cXN2czFtYmJoYWY3MWRkZjlxZWFraXQ4dWdAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&color=%234285F4&color=%23F4511E&color=%2333B679&color=%23D50000&showTitle=0&mode=WEEK&dates={date_range}"
    response = rq.get(url)
    soup = BeautifulSoup(response.text)

    # Set Flag
    flag = False
    week_list = []
    skip_set = set()

    for tr in soup.select("tr")[2:]:
        if tr.get("class") != ['grid-row']:
            # 若已抓得資料，則離開迴圈
            if flag:
                break
            # 日期
            # 建立暫時存放當週日期的 List
            temp_list = []
            # 檢查每一格日期
            for td in tr.select(".date-marker"):
                if "date-not-month" in td.get("class"):
                    # 非本月
                    pointer_day = int(td.contents[0])
                    continue
                else:
                    # 本月
                    # 取得日期數值
                    pointer_day = int(td.contents[0])
                    if pointer_day == curr_date.day:
                        flag = True
                temp_list.append(pointer_day)
            if flag:
                # 若為本週則設為最終結果的 key
                week_list = temp_list[:]
        elif flag:
            # 活動內容
            # 抓出每一格的活動內容
            local_skip_set = set()
            events = tr.select("td")
            duration = 0
            # 同一個 Row
            for i in range(len(events)):
                event = events[i]
                event_duration = 1
                if event.get("colspan"):
                    event_duration = int(event.get("colspan"))
                if event.get("class") and "cell-empty" in event.get("class"):
                    if "cell-last-row" in event.get("class"):
                        # 尋找移除的 index
                        temp_i = -1
                        for n in range(7):
                            if n not in skip_set:
                                temp_i += 1
                            if temp_i == i:
                                local_skip_set.add(n + duration)
                                break
                    continue
                else:
                    item_content = event.select(".item-content")[0]
                    if "event-singleday" in item_content.get("class"):
                        event_time = item_content.select(
                            ".event-time")[0].contents[0]
                        event_content = item_content.select(
                            ".event-summary")[0].contents[0]
                    else:
                        event_time = f"{event_duration} days"
                        event_content = item_content.select(
                            ".event-summary")[0].contents[0]
                    if event_content.find("[") != -1 and event_content.find("]") != -1:
                        category = event_content[event_content.find(
                            "[")+1:event_content.find("]")]
                        event_content = event_content[event_content.find(
                            "]")+1:]
                    else:
                        category = ""
                    # 尋找插入點
                    temp_i = -1
                    for n in range(7):
                        if n not in skip_set:
                            temp_i += 1
                        if temp_i == i:
                            insert_index = n + duration
                            break
                    for j in range(event_duration):
                        # # Print to check code
                        # print(f"Current Skip set: {skip_set}")
                        # print(f"Current Insert Index: {insert_index}")
                        # print(f"Insert {event_content} in  Index {insert_index+j}, Loop {j}-th")
                        result[insert_index +
                               j].append([event_time, category, event_content])
                if event.get("colspan"):
                    duration = duration + event_duration - 1
            for each in local_skip_set:
                skip_set.add(each)
    # 回傳結果
    result.insert(0, week_list)
    return result
