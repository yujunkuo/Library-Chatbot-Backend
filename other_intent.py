## Other Intent Handler class

import numpy as np
import torch

from ckiptagger import WS
from googletrans import Translator

from sentence_transformers import SentenceTransformer
from transformers import BertForQuestionAnswering, BertTokenizer


class OtherIntentHandler:

    def __init__(self):
        self._ws = WS("./ckip")
        self._qa_model = BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
        self._tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
        self._translator = Translator()
        self._sbert_model = SentenceTransformer("distiluse-base-multilingual-cased")
        self._corpuses = self._get_corpuses()
    
    # (Public function) The API which is used to get the answer of other question
    def get_answer(self, sentence: str):
        for corpus in self._corpuses:
            answer = _handle_other_question(sentence, corpus)
            if answer:
                return answer
        return "找不到答案"
    
    # (Protected function) Use input sentence and corpus to get the answer
    def _handle_other_question(self, question_ch: str, text_ch: str):
        # Convert question and text to English
        question_list, question_en = self._trans_from_ch_to_en_with_list(question_ch)
        text_list, text_en = self._trans_from_ch_to_en_with_list(text_ch)
        # Construct Token embedding
        ids_en = self._tokenizer.encode(question_en, text_en)
        tokens_en = self._tokenizer.convert_ids_to_tokens(ids_en)
        # Construct Segment embedding
        sep_index = ids_en.index(self._tokenizer.sep_token_id)
        num_seg_a = sep_index + 1
        num_seg_b = len(ids_en) - num_seg_a
        segment_ids_en = [0]*num_seg_a + [1]*num_seg_b
        # Model Prediction
        start_scores, end_scores = self._qa_model(torch.tensor(
            [ids_en]), token_type_ids=torch.tensor([segment_ids_en]))
        # Find the answer
        answer_start = torch.argmax(start_scores)
        answer_end = torch.argmax(end_scores)
        answer_en = tokens_en[answer_start]
        for i in range(answer_start+1, answer_end+1):
            if tokens_en[i][0:2] == '##':
                answer_en += tokens_en[i][2:]
            elif tokens_en[i] in (",", ".", ":", ";", "!", "?", "'"):
                answer_en += tokens_en[i]
            # To solve he's, they're, I'm ...
            elif i >= 1 and tokens_en[i-1] == "'" and tokens_en[i] in ("s", "m", "re"):
                answer_en += tokens_en[i]
            # To solve 2,000 like number value format
            elif i >= 1 and tokens_en[i-1] == ",":
                try:
                    _ = int(tokens_en[i])
                    answer_en += tokens_en[i]
                except ValueError:
                    answer_en += " " + tokens_en[i]
            else:
                answer_en += " " + tokens_en[i]
        answer_en = answer_en.lower()
        if "[cls]" in answer_en or "[sep]" in answer_en or not answer_en:
            return None
        curr_substring_en, curr_substring_ch = "", ""
        curr_substring_en_list, curr_substring_ch_list = [], []
        for i in range(len(text_list)):
            curr_substring_en = curr_substring_en + ", " + text_list[i][1]
            curr_substring_ch = curr_substring_ch + "，" + text_list[i][0]
            curr_substring_en_list.append(text_list[i][1])
            curr_substring_ch_list.append(text_list[i][0])
            if answer_en in curr_substring_en:
                break
        curr_substring_en = curr_substring_en[1:]
        curr_substring_ch = curr_substring_ch[1:]
        for i in range(len(text_list)):
            curr_substring_en = curr_substring_en[len(text_list[i][1])+2:]
            curr_substring_ch = curr_substring_ch[len(text_list[i][0])+1:]
            curr_substring_en_list.pop(0)
            curr_substring_ch_list.pop(0)
            if answer_en not in curr_substring_en or not curr_substring_en_list:
                curr_substring_en = text_list[i][1] + ", " + curr_substring_en
                curr_substring_ch = text_list[i][0] + "，" + curr_substring_ch
                curr_substring_en_list.insert(0, text_list[i][1])
                curr_substring_ch_list.insert(0, text_list[i][0])
                break
        if not curr_substring_en_list:
            return None
        elif len(curr_substring_en_list) == 1:
            if curr_substring_en_list[0] == answer_en:
                return curr_substring_ch_list[0]
            else:
                final_answer_ch = self._get_ch_ans_from_en_text_from_any_pos(
                    curr_substring_ch_list[0], answer_en)
                return final_answer_ch
        elif len(curr_substring_en_list) == 2:
            if (curr_substring_en_list[0] + ", " + curr_substring_en_list[1]) == answer_en:
                return curr_substring_ch_list[0] + "，" + curr_substring_ch_list[1]
            else:
                start = self._get_ch_ans_from_en_text_from_end(
                    curr_substring_ch_list[0], curr_substring_en_list[0])
                end = self._get_ch_ans_from_en_text_from_start(
                    curr_substring_ch_list[1], curr_substring_en_list[1])
                final_answer_ch = start + "，" + end
                return final_answer_ch
        else:
            start = self._get_ch_ans_from_en_text_from_end(
                curr_substring_ch_list[0], curr_substring_en_list[0])
            end = self._get_ch_ans_from_en_text_from_start(
                curr_substring_ch_list[-1], curr_substring_en_list[-1])
            middle = "，".join(curr_substring_ch_list[1:-1])
            final_answer_ch = "{}，{}，{}".format(start, middle, end)
            return final_answer_ch

    # (Protected function) Translation function: Chinese -> English
    # which will return "en-ch translation pair" & "English text" simultaneously
    def _trans_from_ch_to_en_with_list(self, ch_text: str):
        for ch in ["。", "、", "；", "：", "！", "？", "!", "?"]:
            ch_text = ch_text.replace(ch, "，")
        ch_text_list = [text for text in ch_text.split("，") if text]
        en_trans = self._translator.translate(ch_text_list, dest='en')
        en_text_list = [tran.text.lower() for tran in en_trans]
        en_text = ", ".join(en_text_list)
        tran_list = [(ch_text, en_text)
                    for ch_text, en_text in zip(ch_text_list, en_text_list)]
        return (tran_list, en_text)

    # (Protected function) Translation function: Chinese -> English
    def _trans_from_ch_to_en(self, ch_text: str):
        en_tran = self._translator.translate(ch_text, dest='en')
        en_text = en_tran.text.lower()
        return en_text

    # (Protected function)
    def _get_ch_ans_from_en_text_from_any_pos(self, ch_text, en_text):
        en_embedding = self._sbert_model.encode(en_text)
        candidate, candidate_sim = None, -1
        ckip_ch_text = self._ws([ch_text])[0]
        for i in range(len(ckip_ch_text)):
            for j in range(i+1, len(ckip_ch_text)+1):
                curr_ch_text = "".join(ckip_ch_text[i:j])
                candidate_en_text = self._trans_from_ch_to_en(curr_ch_text)
                candidate_en_embedding = self._sbert_model.encode(candidate_en_text)[0]
                sim = self._cal_cosine_sim(en_embedding, candidate_en_embedding)[0]
                # larger or equal will become candidate, since it will let the result better!
                if round(sim, 4) >= round(candidate_sim, 4):
                    candidate_sim = sim
                    candidate = curr_ch_text
                    # if sim > 0.95:
                    #     return candidate
        return candidate

    # (Protected function)
    def _get_ch_ans_from_en_text_from_start(self, ch_text, en_text):
        en_embedding = self._sbert_model.encode(en_text)
        candidate, candidate_sim = None, -1
        ckip_ch_text = self._ws([ch_text])[0]
        for i in range(1, len(ckip_ch_text)+1):
            curr_ch_text = "".join(ckip_ch_text[:i])
            candidate_en_text = self._trans_from_ch_to_en(curr_ch_text)
            candidate_en_embedding = self._sbert_model.encode(candidate_en_text)[0]
            sim = self._cal_cosine_sim(en_embedding, candidate_en_embedding)[0]
            # larger or equal will become candidate, since it will let the result better!
            if round(sim, 4) >= round(candidate_sim, 4):
                candidate_sim = sim
                candidate = curr_ch_text
        return candidate

    # (Protected function)
    def _get_ch_ans_from_en_text_from_end(self, ch_text, en_text):
        en_embedding = self._sbert_model.encode(en_text)
        candidate, candidate_sim = None, -1
        ckip_ch_text = self._ws([ch_text])[0]
        for i in range(len(ckip_ch_text)):
            curr_ch_text = "".join(ckip_ch_text[i:])
            candidate_en_text = self._trans_from_ch_to_en(curr_ch_text)
            candidate_en_embedding = self._sbert_model.encode(candidate_en_text)[0]
            sim = self._cal_cosine_sim(en_embedding, candidate_en_embedding)[0]
            # larger or equal will become candidate, since it will let the result better!
            if round(sim, 4) >= round(candidate_sim, 4):
                candidate_sim = sim
                candidate = curr_ch_text
        return candidate
    
    # (Protected function) Calculate Cosine Similarity between to sentences
    def _cal_cosine_sim(self, x, y):
        res = np.dot(x, y) / (np.linalg.norm(x)*np.linalg.norm(y))
        return res
    
    # (Protected function) Get those corpuses which are used to find the answer
    def _get_corpuses(self):
        corpus_1 = """
        大學圖書館為學生課後最常駐足停留的場所，圖書館的主要功能即在於提供豐富的資源、完善的環境、多元的服務，以支援師生教學、研究與學習需求。隨著資訊科技的迅速發展，網路世代(Net Generation)讀者成為大學圖書館主要服務對象，故圖書館應轉型以提供資訊服務為核心，結合建築空間及管理策略，開創符合時代趨勢的數位化圖書館。
        政大圖書館館藏量位居國內大學圖書館第二名，為人文社會科學資源典藏與研究重鎮，然而在數位時代快速變遷下，中正圖書館與分館的空間已達飽和，難以再規畫新穎的學習共享空間，建築硬體亦無法配合資訊科技的發展而受限，加上建築承載安全性隱憂，使本校圖書館面臨發展的瓶頸。
        政大圖書館自民94年起著手進行中正圖書館整建、擴建之可行性研究；民98年繼之為後山張家古厝藏書樓規劃；此外，與台灣大學圖書館、台灣師範大學圖書館、國家圖書館等共同向教育部提出聯合藏書樓計畫；民101年參與學校書院宿舍構想書之規劃，以上各項努力皆因不同的因素未能落實。
        """
        corpus_2 = """
        民國99年行政院終於同意將政大多年爭取、鄰近校園占地約10餘公頃之國防部指南山莊營區，正式核撥予政大；民104年政治大學正式取得指南山莊；民105年幸得校友慨捐指南山莊全區規劃以及圖書館建築，捐贈者感念恩師司徒達賢老師的教導，命名為「達賢圖書館」。
        達賢圖書館位於指南山莊校區最前端，在指南山莊校區規劃裡，未來對面將設置捷運站，後方則環繞新建宿舍，成為校園的新地標。達賢圖書館主棟為地下二樓，地上八樓的建築，於民105年8月份確定建築面積為27,000餘平方公尺，扣除地下一樓汽車停車場及一樓機車停車場，圖書館使用樓層為B2密集書庫及2-7樓空間，面積約為15,432平方公尺。離主棟建築不遠處另有一棟湖濱悅讀小屋，容納300多個自修席位，達賢圖書館規畫主軸為：
        資訊多樣化(多元軟硬體與新科技探索)、學習共享空間(人與己、人與社群、人與資料之對話交流空間)與特色館藏(結合數位典藏成果，建置專業典藏環境、多元收藏展品、科技展演展示空間， 擴大研究資源、擴展研究能量)。
        """
        corpus_3 = """
        達賢圖書館擬型塑 My READ, My libray 理念
        R代表Research Education，支援學術深化與研究協作。
        E代表Exploration，圖書館資源提供讀者探索。
        A代表Aspiration，提供創意激盪與實驗的空間。
        D代表Diversity，多樣化的資源與服務滿足師生教學、研究與學習需求。
        """
        corpus_4 = """
        達賢圖書館的借還書籍與視聽資料服務的開放時間:週一到週五為08:30至17:30，週六為10:00至17:30，週日閉館不提供服務。
        達賢圖書館的主棟二到八樓的開放時間:週一到週六為08:00至18:00，週日閉館不提供服務。
        達賢圖書館的湖濱小屋一樓的開放時間:週一到週六為08:00至18:00，週日閉館不提供服務。
        達賢圖書館的四樓資訊教室的開放時間:週一到週五為08:30至17:30，週六為10:00至17:30，週日閉館不提供服務。
        達賢圖書館的五樓創客空間的開放時間:週一到週五為09:00至17:00，週六與週日閉館不提供服務。
        達賢圖書館的二樓特藏中心的開放時間:週一到週五為08:30至17:00，週六與週日閉館不提供服務。
        """
        corpus_5 = """
        如果要去達賢圖書館，可以搭公車66、236、282、295、611、綠1、棕15、棕18至萬興圖書館站下車，或530、棕11至指南山莊站，再步行3-5分鐘即可到達。
        """
        corpuses = [corpus_4, corpus_5, corpus_1, corpus_2, corpus_3]
        return corpuses
