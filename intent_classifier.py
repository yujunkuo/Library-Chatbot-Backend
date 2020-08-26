## Intent classification class

import torch

from transformers import BertTokenizer
from transformers import BertForSequenceClassification


class IntentClassifier:

    def __init__(self):
        self._tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
        self._model = BertForSequenceClassification.from_pretrained("./models/intent_model/")
        self._label_map = {"search_book": 0, "borrow_place": 1, "other": 2}
        self._index_map = {v: k for k, v in self._label_map.items()}

    # (Public function) This is the API for Intent Classification
    def get_intent_classification(self, sentence: str):
        sentence_tensor = self._get_sentence_tensor(sentence)
        pred = self._get_sentence_pred(sentence_tensor)
        final_pred = self._index_map[int(pred[0])]
        return final_pred

    # (Protected function) Which is used to get sentence tensor
    def _get_sentence_tensor(self, sentence: str):
        # 建立句子的 BERT tokens
        sentence_tokens = self._tokenizer.tokenize(sentence)
        word_pieces = ["[CLS]"] + sentence_tokens + ["[SEP]"]
        word_pieces_len = len(word_pieces)
        # 將整個 token 序列轉換成索引序列
        ids = self._tokenizer.convert_tokens_to_ids(word_pieces)
        # Token Tensor
        token_tensor = torch.tensor(ids)
        # Segment Tensor
        segment_tensor = torch.tensor([0] * word_pieces_len, dtype=torch.long)
        # Mask Tensor
        mask_tensor = torch.tensor([1] * word_pieces_len, dtype=torch.long)
        # Label Tensor
        label_tensor = None
        return (token_tensor, segment_tensor, mask_tensor, label_tensor)

    # (Protected function) Which is used to get sentence prediction
    def _get_sentence_pred(self, sentence_tensor: tuple):
        predictions = None
        correct = 0
        total = 0
        
        with torch.no_grad():

            # 將所有 tensors 移到 GPU 上
            if next(self._model.parameters()).is_cuda:
                sentence_tensor = [t.to("cuda:0") for t in sentence_tensor if t is not None]
            
            # 前 3 個 tensors 分別為 token, segment 以及 mask
            # 建議在將這些 tensors 丟入 model 時指定對應的參數名稱
            token_tensor, segment_tensor, mask_tensor = sentence_tensor[:3]
            token_tensor = token_tensor.resize_((1, token_tensor.shape[0]))
            segment_tensor = segment_tensor.resize_((1, segment_tensor.shape[0]))
            mask_tensor = mask_tensor.resize_((1, mask_tensor.shape[0]))
            outputs = self._model(input_ids=token_tensor, 
                            token_type_ids=segment_tensor, 
                            attention_mask=mask_tensor)
            
            logits = outputs[0]
            _, pred = torch.max(logits.data, 1)

        return pred
