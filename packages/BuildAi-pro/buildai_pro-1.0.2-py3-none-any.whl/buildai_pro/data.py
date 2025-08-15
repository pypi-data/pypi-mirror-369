from typing import List, Tuple
import numpy as np
class Tokenizer:
    def __init__(self, lower=True, unk_token='<UNK>'):
        self.lower = lower
        self.unk = unk_token
        self.vocab = {self.unk:0}
    def fit_on_texts(self, texts:List[str]):
        idx = len(self.vocab)
        for t in texts:
            s = t.lower() if self.lower else t
            for w in s.split():
                if w not in self.vocab:
                    self.vocab[w] = idx; idx += 1
    def texts_to_sequences(self, texts:List[str]):
        seqs = []
        for t in texts:
            s = t.lower() if self.lower else t
            seqs.append([self.vocab.get(w, 0) for w in s.split()])
        return seqs
    def vocab_size(self):
        return len(self.vocab)
def pad_sequences(seqs:List[List[int]], maxlen:int=None, padding='post', value=0):
    if maxlen is None:
        maxlen = max(len(s) for s in seqs) if seqs else 0
    out = []
    for s in seqs:
        if len(s) < maxlen:
            if padding=='post':
                out.append(s + [value]*(maxlen-len(s)))
            else:
                out.append([value]*(maxlen-len(s)) + s)
        else:
            out.append(s[:maxlen])
    return np.array(out, dtype=int)
class TextDataset:
    def __init__(self, texts:List[str], labels:List[int], tokenizer:Tokenizer=None):
        self.tokenizer = tokenizer or Tokenizer()
        self.tokenizer.fit_on_texts(texts)
        self.seqs = self.tokenizer.texts_to_sequences(texts)
        self.labels = labels
    def to_numpy(self, maxlen:int=None):
        X = pad_sequences(self.seqs, maxlen=maxlen)
        y = np.array(self.labels, dtype=int)
        return X, y
