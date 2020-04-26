from copy import deepcopy

import torch
import torch.utils.data as data
import json


class SimpleVocab(object):
    def __init__(self, items):
        cnt = 0
        self.token2Idx = {}
        self.idx2Topic = {}
        for topic in items:
            self.token2Idx[topic] = cnt
            self.idx2Topic[cnt] = topic
            cnt += 1
    def convertIdx2Token(self, idx):
        return torch.tensor(self.idx2Topic[idx])
    def convertTokens2Idxs(self, tokens):
        return torch.stack([self.convertToken2Idx(token) for token in tokens], dim=0)
    def convertToken2Idx(self, token):
        return torch.tensor(self.topic2Idx[token])



class BCDataset(data.Dataset):
    def __init__(self, docs, tag_isRelated, tag_clarity, tag_usefulness, topics, topicIdx):
        super(BCDataset, self).__init__()
        self.docs = docs
        self.tag_isRelated = tag_isRelated
        self.tag_clarity = tag_clarity
        self.tag_usefulness = tag_usefulness
        self.topics = topics
        self.topicIdx = topicIdx
        # print(topicIdx)
        self.size = len(docs)
    def __len__(self):
        return self.size
    def __getitem__(self, index):
        doc = deepcopy(self.docs[index])
        isRelated = deepcopy(self.tag_isRelated[index])
        clarity = deepcopy(self.tag_clarity[index])
        usefulness = deepcopy(self.tag_usefulness[index])
        topics = deepcopy(self.topics[index])
        return doc, (isRelated, clarity, usefulness, topics)
    def getTopicIdx(self):
        return self.topicIdx
    @staticmethod
    def loadData(file, tokenize, convertToken2Idx):
        with open(file) as f:
            items = f.readlines()
            items = [json.loads(item) for item in items]
        docs = []
        tag_isRelated = []
        tag_clarity = []
        tag_usefulness = []
        topics = []
        topicIdx = None
        for item in items:
            # print(item)
            sents = item["text"].split('\n')
            for idx in range(len(sents)):
                # print(sents[idx])
                sents[idx] = ['[CLS]'] + tokenize(sents[idx])
                # print(sents[idx])
            # sents = [tokenize(sent) for sent in sents]
            sents = [torch.tensor(convertToken2Idx(sent)) for sent in sents]
            docs.append(sents)
            tag_isRelated.append(torch.tensor([item["tags"]["COVID-19関連"]], dtype=torch.float))
            tag_clarity.append(torch.tensor([item["tags"]["clarity"]], dtype=torch.float))
            tag_usefulness.append(torch.tensor([item["tags"]["usefulness"]], dtype=torch.float))
            if topicIdx is None:
                topicIdx = list(item["tags"]["topic"].keys())
            # print(topicIdx)
            topics.append(torch.tensor([tuple[1]for tuple in item["tags"]["topic"].items()], dtype=torch.float))
        return BCDataset(docs, tag_isRelated, tag_clarity, tag_usefulness, topics, topicIdx)


